import os
import shutil
import subprocess
import tempfile
import wave

import requests
from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END 
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage # The foundational class for all message types in LangGraph 
from langgraph.graph.message import add_messages # Allows to append all messages to the state without overriding any of it 
from typing import TypedDict, Annotated, Sequence

load_dotenv()

# This is the global variable to store document content 
document_content = ""
interaction_mode = "text"
displayed_tool_messages = set()


class VoiceIO:
    """Record speech, transcribe it with Groq, and speak with ElevenLabs."""

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        # Voice output uses the standard ElevenLabs environment variable name.
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
        self.tts_model = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
        self.transcription_model = os.getenv(
            "GROQ_TRANSCRIPTION_MODEL", "whisper-large-v3-turbo"
        )
        self.sample_rate = 16_000

    def listen(self) -> str:
        """Capture microphone audio until Enter is pressed and return its text."""
        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required for voice transcription.")

        try:
            import sounddevice as sd
        except ImportError as exc:
            raise RuntimeError(
                "Voice input requires sounddevice. Install it with: "
                "venv/bin/python -m pip install sounddevice"
            ) from exc

        frames = []

        def capture(indata, frame_count, time_info, status):
            del frame_count, time_info
            if status:
                print(f"\nMicrophone warning: {status}")
            frames.append(bytes(indata))

        print("\n🎙️  Listening... press Enter when you are finished speaking.")
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16",
                callback=capture,
            ):
                input()
        except Exception as exc:
            raise RuntimeError(f"Could not record from the microphone: {exc}") from exc

        if not frames:
            raise RuntimeError("No microphone audio was captured.")

        audio_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
                audio_path = audio_file.name

            with wave.open(audio_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(b"".join(frames))

            try:
                client = Groq(api_key=self.groq_api_key)
                with open(audio_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        file=audio_file,
                        model=self.transcription_model,
                        response_format="json",
                        temperature=0.0,
                    )
                return transcription.text.strip()
            except Exception as exc:
                raise RuntimeError(f"Could not transcribe the recording: {exc}") from exc
        finally:
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)

    def speak(self, text: str) -> None:
        """Generate speech with ElevenLabs and play it through the speakers."""
        text = text.strip()
        if not text:
            return

        if not self.elevenlabs_api_key:
            self._system_speak(text)
            return

        audio_path = None
        try:
            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
                params={"output_format": "mp3_44100_128"},
                headers={
                    "xi-api-key": self.elevenlabs_api_key,
                    "Content-Type": "application/json",
                },
                json={"text": text[:4_000], "model_id": self.tts_model},
                timeout=60,
            )
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
                audio_file.write(response.content)
                audio_path = audio_file.name

            self._play(audio_path)
        except requests.RequestException as exc:
            print(f"\nVoice output warning: ElevenLabs failed ({exc}).")
            self._system_speak(text)
        finally:
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)

    @staticmethod
    def _play(audio_path: str) -> None:
        player = shutil.which("afplay") or shutil.which("mpg123") or shutil.which("ffplay")
        if not player:
            print("\nVoice output warning: no MP3 audio player was found.")
            return

        command = [player, audio_path]
        if os.path.basename(player) == "ffplay":
            command = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", audio_path]
        subprocess.run(command, check=False)

    @staticmethod
    def _system_speak(text: str) -> None:
        """Use macOS speech as a no-key fallback for voice output."""
        say = shutil.which("say")
        if say:
            subprocess.run([say, text[:4_000]], check=False)
        else:
            print("\nVoice output is unavailable. Set ELEVENLABS_API_KEY to enable it.")


voice_io = VoiceIO()

# injected State - NEyond this course STILL NEED TO LEARN WHAT IS AND HOW TO USE IT

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages]

@tool
def update(content : str) -> str: # This parameters will get provided by the LLm in the background
    """ Update the document with the provided content """
    global document_content
    document_content = content
    return f"Document has been updated successfully! The current content is:\n{document_content}"

@tool
def save(filename : str) -> str:
    """ Save the current document to a text file and finisht he process.
    
    Args:
        filename: Name for the text file
    """

    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"

    try: 
            with open(filename, 'w') as file: 
                file.write(document_content)
            print(f"\nDocument has been saved to: {filename}")
            return f"Document has been saved successfully to '{filename}'."
    except Exception as e:
         return f"Error saving document: {str(e)}"


our_tools = [update, save]

llm = ChatGroq(
    model = "openai/gpt-oss-120b",
    temperature= 0.0,
    groq_api_key = os.getenv("GROQ_API_KEY")
)

model = llm.bind_tools(our_tools)


def get_user_input() -> str:
    """Read typed input or, in voice mode, record speech when Enter is pressed."""
    global interaction_mode

    while True:
        if interaction_mode == "voice":
            typed_input = input(
                "\nType a message, press Enter to speak, or enter /text: "
            ).strip()
            if typed_input == "/text":
                interaction_mode = "text"
                print("⌨️  Text mode enabled.")
                continue
            if typed_input:
                return typed_input

            try:
                transcript = voice_io.listen()
                if transcript:
                    print(f"\n👤 YOU SAID: {transcript}")
                    return transcript
                print("I did not hear any speech. Please try again.")
            except RuntimeError as exc:
                print(f"\nVoice input error: {exc}")
                print("Switching to text mode.")
                interaction_mode = "text"
        else:
            typed_input = input(
                "\nWhat would you like to do with the document? "
                "(enter /voice for voice mode) "
            ).strip()
            if typed_input == "/voice":
                interaction_mode = "voice"
                print("🎙️  Voice mode enabled. You can still type whenever you want.")
                continue
            if typed_input:
                return typed_input

def our_agent_node(state : AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
    
    - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to always show the current document state after modifications.
    
    The current document content is:{document_content}
    """)

    if not state['messages']:
        user_input = "I'm ready to help you update a document. What would you like to create?"
        user_message = HumanMessage(content = user_input)

    else: 
        user_input = get_user_input()
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content = user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = model.invoke(all_messages)

    print(f"\n🤖 AI: {response.content}")
    if interaction_mode == "voice" and response.content:
        voice_io.speak(str(response.content))
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔧 USING TOOLS: {[tc['name'] for tc in response.tool_calls]}\n")

    return {'messages' : list(state['messages']) + [user_message, response]}

def should_continue(state : AgentState):
    """ Determine if we should continue or end the conversation  """ 
    messages = state['messages']

    if not messages:
        return "continue"

    # This looks for the most recent tools message
    for message in reversed(messages): # Checks the latest message in the chat
        # Checks if this is a ToolMessage resulting from save
        if (isinstance(message, ToolMessage) # Ensures the message is an output  generated by an executed tool rather than a prompt from the HumanMEssage or a response form an AIMessage
            and "saved" in message.content.lower() # Lowercase the response so it catches all 'saved' posibilities if appears anywhere in the tools return string
            and "document" in message.content.lower()): # Same 
            return "end" # Goes to the end edge which leads to the endpoint

    return "continue"

def print_messages(messages):
    """Function I made to print the messages in a more readable format"""
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            message_key = message.tool_call_id or message.id
            if message_key in displayed_tool_messages:
                continue
            displayed_tool_messages.add(message_key)
            print(f"\n🔧 TOOL RESULT: {message.content}")
            if interaction_mode == "voice":
                voice_io.speak(str(message.content))

graph = StateGraph(AgentState)

graph.add_node("agent", our_agent_node)
graph.add_node("tools", ToolNode(our_tools))

graph.set_entry_point("agent")

graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue" : "agent",
        "end" : END
    }
)

agent = graph.compile()

def run_document_agent():
    global interaction_mode

    displayed_tool_messages.clear()
    print("\n ===== DRAFTER =====")
    selected_mode = input("Choose a mode: [t]ext or [v]oice (default: text): ").strip().lower()
    interaction_mode = "voice" if selected_mode in {"v", "voice"} else "text"
    if interaction_mode == "voice":
        print("🎙️  Voice mode enabled. Press Enter to speak or type a message.")
    else:
        print("⌨️  Text mode enabled. Enter /voice at any time to switch.")
    
    state = {"messages": []}
    
    for step in agent.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    
    print("\n ===== DRAFTER FINISHED =====")

if __name__ == "__main__":
    run_document_agent()

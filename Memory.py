import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv() # Function to load the key

CONTEXT_WINDOW = 5 # Number of complete user + AI exchanges to remember

llm = ChatGroq( # Loads the actual model we're trying to use 
    model = "openai/gpt-oss-120b",
    temperature = 0.0,
    groq_api_key = os.getenv("GROQ_API_KEY")
)

class AgentState(TypedDict): # Create the class for the agent
    messages : List[Union[HumanMessage, AIMessage]]

def process_node(state : AgentState) -> AgentState: # Create the first node
    """ This code will solve the request you input"""
    response = llm.invoke(state['messages']) # contains both messages, either AI or Human

    state['messages'].append(AIMessage(content = response.content)) # .content retieves only the important part of the answer, not the whole process
    print(f"\nAI: {response.content}")

    print("CURRENT STAE: ", state['messages'])

    return state

graph = StateGraph(AgentState)
graph.add_node("process", process_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

conversation_history = [] # Only the messages the agent currently remembers
conversation_log = [] # The complete conversation, used for logging

user_input = input("Enter: ")
while user_input != "exit":
    human_message = HumanMessage(content=user_input)
    conversation_history.append(human_message)
    conversation_log.append(human_message)

    # Leave room for the AI response so the completed context stays at 5 pairs.
    conversation_history = conversation_history[-(CONTEXT_WINDOW * 2 - 1):]
    result = agent.invoke({"messages": conversation_history})
    conversation_history = result["messages"][-(CONTEXT_WINDOW * 2):]
    conversation_log.append(conversation_history[-1])
    user_input = input("Enter: ")

with open("logging.txt", "w") as file:
    file.write("Your Conversation Log:\n")
    
    for message in conversation_log:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation")

print("Conversation saved to logging.txt")

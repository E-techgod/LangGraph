import os
import warnings
import logging
from operator import add as add_messages  # Use for gathering raw search results

from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from transformers import logging as hf_logging

warnings.filterwarnings("ignore")  # Silence all warnings (UserWarning, DeprecationWarning, etc.)

# Tell Hugging Face Hub not to prompt or warn about missing tokens
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_TOKEN"] = ""  # Or export HF_HUB_DISABLE_IMPLICIT_TOKEN=1

logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
hf_logging.set_verbosity_error()

from typing import TypedDict, Annotated, Sequence

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

llm = ChatGroq(
    model = "openai/gpt-oss-120b",
    temperature = 0,
    groq_api_key = os.getenv("GROQ_API_KEY")
)

# Embedding model has to be also competitive with our LLM 
embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True}
)

pdf_path = "Stock_Market_Performance_2024.pdf"

# Checks if the poath exists 
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found: {pdf_path}")

pdf_loader = PyPDFLoader(pdf_path) # This loads the pdf

# Checks if the PDF is there 
try: 
    pages = pdf_loader.load()
    print(f"PDF has been loaded has {len(pages)} pages")
except Exception as e:
    print(f"Error loading PDF: {e}")
    raise 

# Chunking process
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)

pages_split = text_splitter.split_documents(pages) # We now apply this to our pages

persist_directory = r'/Users/eliasarellanocampos/EAC/LangGraph'
collection_name = "stock_market"

# If our collection does not exist in the directory, we create using the os command
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

try:
    # Here, we actually create the chroma database using our embeddigns model
    vectorstore = Chroma.from_documents(
        documents=pages_split,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    print(f"Created ChromaDB vector store!")
    
except Exception as e:
    print(f"Error setting up ChromaDB: {str(e)}")
    raise

retriever = vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k" : 5} # K is the amount of chunks to return 
)

@tool
def retriever_tool(query : str) -> str:
    """
    This tool searches and returns the information from the Stock Market Performance 2024 document.
    """

    docs = retriever.invoke(query)

    if not docs:
        return "I found no relevant information in the Stock Marker Performance 2024 document."

    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}: \n{doc.page_content}")

    return "\n\n".join(results)

our_tools = [retriever_tool]

llm = llm.bind_tools(our_tools)

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages]

def should_continue(state : AgentState):
    """ Check if the last message contains tool calls."""
    result = state['messages'][-1]
    return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0

system_prompt = """
You are an intelligent AI assistant who answers questions about Stock Market Performance in 2024 based on the PDF document loaded into your knowledge base.
Use the retriever tool available to answer questions about the stock market performance data. You can make multiple calls if needed.
If you need to look up some information before asking a follow up question, you are allowed to do that!
Please always cite the specific parts of the documents you use in your answers.
"""

tools_dict = {our_tool.name: our_tool for our_tool in our_tools} # Creating a dictionary of our tools

# LLM Agent
def call_llm_node(state : AgentState) -> AgentState:
    """Function to call the LLM with the current state"""
    messages = list(state['messages'])
    messages = [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)
    return {'messages' : [message]}

# Retriever Agent
def take_action_node(state: AgentState) -> AgentState:
    """Execute tool calls from the LLM's response."""

    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        print(f"Calling Tool: {t['name']} with query: {t['args'].get('query', 'No query provided')}")
        
        if not t['name'] in tools_dict: # Checks if a valid tool is present
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
        
        else:
            result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            print(f"Result length: {len(str(result))}")
            

        # Appends the Tool Message
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools Execution Complete. Back to the model!")
    return {'messages': results}

graph = StateGraph(AgentState)

graph.add_node("llm", call_llm_node)
graph.add_node("retriever_agent", take_action_node)

graph.add_conditional_edges(
    "llm",
    should_continue,
    {
        True: "retriever_agent",
        False: END
    }
)

graph.add_edge("retriever_agent", "llm")
graph.set_entry_point("llm")

rag_agent = graph.compile()

def running_agent():
    print("\n=== RAG AGENT===")

    while True: 
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        messages = [HumanMessage(content = user_input)] # Converts back to a HumanMEssage type

        results = rag_agent.invoke({'messages' : messages})

        print("\n=== ANSWER ===")
        print(results['messages'][-1].content)

if __name__ == "__main__":
    running_agent()
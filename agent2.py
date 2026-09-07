import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage 

load_dotenv() # Function to load the key

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

    state['messages'].append(AIMessage(content= response.content)) # .content retieves only the important part of the answer, not the whole process
    print(f"\nAI: {response.content}")

    return state
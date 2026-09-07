import os
from dotenv import load_dotenv
from typing import TypedDict, List
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

load_dotenv()

class AgentState(TypedDict):
    messages : List[HumanMessage]

llm = ChatGroq(
    model = "openai/gpt-oss-120b", 
    temperature = 0.0,
    groq_api_key = os.getenv("GROQ_API_KEY")
)


def process(state : AgentState) -> AgentState:
    response = llm.invoke(state['messages'])

    print(f"\nAI: {response.content}")
    return state 

graph = StateGraph(AgentState)

graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()

user_input = input("Enter: ")
while user_input != "exit": 
    agent.invoke({'messages' : [HumanMessage(content=user_input)]})
    user_input = input("Enter: ")

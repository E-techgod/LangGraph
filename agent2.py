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

    state['messages'].append(AIMessage(content = response.content)) # .content retieves only the important part of the answer, not the whole process
    print(f"\nAI: {response.content}")

    return state

graph = StateGraph(AgentState)
graph.add_node("process", process_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

conversation_history = [] # This is where we'll store the conversation 

user_input = input("Enter: ")
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": conversation_history})
    conversation_history = result["messages"]
    user_input = input("Enter: ")

with open("logging.txt", "w") as file:
    file.write("Your Conversation Log:\n")
    
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation")

print("Conversation saved to logging.txt")
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END 
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph 
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content and tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM 
from langgraph.graph.message import add_messages # Allows to append all messages to the state without overriding any of it 
from typing import TypedDict, Annotated, Sequence

load_dotenv()

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages] # Preserve the state by appending than replacing [DataType, MetaData]

@tool # Decorator
def add(a : int, b : int):
    """ This is an addition function that adds two numbers together"""
    return a + b

@tool
def subtract(a : int, b : int):
    """ This is a subtraction funtion that subtracts two numbers together"""
    return a - b 

@tool
def multiply(a : int, b : int):
    """ This is a multiplicaton funtion that multiplies two numbers together"""
    return a * b 

our_tools = [add, subtract, multiply]

llm = ChatGroq(
    model = "openai/gpt-oss-120b",
    temperature= 0.0,
    groq_api_key = os.getenv("GROQ_API_KEY"),
)

model = llm.bind_tools(our_tools)

def agent_node(state : AgentState) -> AgentState:
    system_prompt = SystemMessage(
        content=(
            "You are my AI assistant, please answer my query to the best of your ability."
            "Every single addition, subtraction, or multiplication MUST be executed using the appropriate tool."
        )
    )
    response = model.invoke([system_prompt] + state['messages']) 
    return {'messages' : [response]}

def should_continue(state : AgentState): # This is not a node, this will guide to the correct node 
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else: 
        return "continue"


graph = StateGraph(AgentState)
graph.add_node("our_agent", agent_node)

tool_node = ToolNode(tools=our_tools) # Tool that contans all the necessary tools 
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue" : "tools",
        "end" : END,
    },
)

graph.add_edge("tools", "our_agent")

agent = graph.compile()

"""png_data = agent.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_data))
image.show()
"""
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {'messages' : [("user", "Add 40 + 12 and then multiply the result by 6. Also tell me a joke please")]}
print_stream(agent.stream(inputs, stream_mode="values"))
import io
from PIL import Image
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    num1 : int
    num2: int
    operation : str
    finalNum : int 

def add_node(state : AgentState) -> AgentState:
    """This node adds 2 nums"""
    return {'finalNum' : state['num1'] + state['num2']}

def subtract_node(state : AgentState) -> AgentState:
    """This node adds 2 nums"""
    return {'finalNum' : state['num1'] - state['num2']}

def decide_next_node(state : AgentState) -> AgentState:
    """This node will select the next phase of the graph"""

    if state['operation'] == "+":
        return "addition_operation"
    elif state['operation'] == "-":
        return "subtraction_operation"

graph = StateGraph(AgentState)

graph.add_node("add", add_node)
graph.add_node("subtract", subtract_node)
graph.add_node("router", lambda state : state) # Passthrough function 

graph.add_edge(START, "router")

graph.add_conditional_edges(
    "router", 
    decide_next_node,

    {
        # Edge : Node
        "addition_operation" : "add",
        "subtraction_operation" : "subtract"
    }
) 

graph.add_edge("add", END)
graph.add_edge("subtract", END)

app = graph.compile()

png_data = app.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_data))
image.show()


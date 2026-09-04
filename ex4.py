import io
from traceback import print_tb
from PIL import Image
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    num1 : int
    num2 : int
    num3 : int
    num4 : int

    op1 : str
    op2 : str

    fnum1 : int
    fnum2 : int

# First part of the graph's nodes
def addition_node(state : AgentState) -> AgentState:
    """ This node will add the first numbers """
    return {'fnum1' : state['num1'] + state['num2']}

def subtraction_node(state : AgentState) -> AgentState:
    """ This node will subtract the first numbers """
    return {'fnum1' : state['num1'] - state['num2']}

def decision_router_node(state : AgentState) -> AgentState:
    """ This node will decide which operation to perform """
    if state['op1'] == "+":
        return "addition_operation" # Edge 
    elif state['op1'] == "-":
        return "subtraction_operation" # Edge 

# Second part of the graph's nodes
def addition_node2(state : AgentState) -> AgentState:
    """ This node will add the first numbers """
    return {'fnum2' : state['num3'] + state['num4']}

def subtraction_node2(state : AgentState) -> AgentState:
    """ This node will subtract the first numbers """
    return {'fnum2' : state['num3'] - state['num4']}

def decision_router_node2(state : AgentState) -> AgentState:
    """ This node will decide which operation to perform """
    if state['op2'] == "+":
        return "addition_operation2" # Edge 
    elif state['op2'] == "-":
        return "subtraction_operation2" # Edge 
    
graph = StateGraph(AgentState)

# Firts part of the graph: Add first nodes
graph.add_node("add_node", addition_node)
graph.add_node("sub_node", subtraction_node)
graph.add_node("router", lambda state : state)

# Second part of the graph: Add second nodes
graph.add_node("add_node2", addition_node2)
graph.add_node("sub_node2", subtraction_node2)
graph.add_node("router2", lambda state : state)

# Add Edge 
graph.add_edge(START, "router")

# First conditional of the graph 
graph.add_conditional_edges(
    "router", decision_router_node,

    {   
        # Edge : Node
        "addition_operation" : "add_node",
        "subtraction_operation" : "sub_node"
    }
)

graph.add_edge("add_node", "router2")
graph.add_edge("sub_node", "router2")

# Second conditional of the graph
graph.add_conditional_edges(
    "router2", decision_router_node2,

    {   
        # Edge : Node
        "addition_operation2" : "add_node2",
        "subtraction_operation2" : "sub_node2"
    }
)

graph.add_edge("add_node2", END)
graph.add_edge("sub_node2", END)

app = graph.compile()

png_data = app.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_data))
image.show()

answer = app.invoke({'num1' : 10, 'op1' : "-", 'num2' : 5, 'num3' : 7, 'num4' : 2, 'op2' : "+"})

print(answer['fnum1'])
print(answer['fnum2'])

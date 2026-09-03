import io
from PIL import Image
from typing import TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict): # 1. Create state
    name : str
    age : str
    result : str

def first_node(state : AgentState) -> AgentState:
    """This is the first node of our sequence"""
    return {'result': f"Hi {state['name']}"}

def second_node(state : AgentState) -> AgentState:
    """This is the second node of our sequence"""
    return {'result' : state['result'] + f". You are {state['age']} years old"}

graph = StateGraph(AgentState)

graph.add_node("first_node", first_node)
graph.add_node("second_node", second_node)

graph.set_entry_point("first_node")
graph.add_edge("first_node", "second_node")
graph.set_finish_point("second_node")

app = graph.compile()

png_data = app.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_data))
image.show()

result = app.invoke({"name" : "Chalry", "age" : "23"})

print(result['result'])
import io
from PIL import Image
from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    name : str
    age : int
    skills : List[str]
    r : str

def name_node(state : AgentState) -> AgentState:
    """This function accepst the name of the user as input"""
    return {'r' : f"{state['age']}, welcome to the system!"}

def age_node(state : AgentState) -> AgentState:
    """This function accepst the age of the user as input"""
    return {'r' : state['r'] + f" You are {state['age']} yeards old!"}

def skills_node(state : AgentState) -> AgentState:
    """This function accepst the skills of the user as input"""
    return {'r' : state['r'] + f" You have skills in: {state['skills']}"}

graph = StateGraph(AgentState)

graph.add_node("name", name_node)
graph.add_node("age", age_node)
graph.add_node("skills", skills_node)

graph.set_entry_point("name")
graph.add_edge("name", "age")
graph.add_edge("age", "skills")
graph.set_finish_point("skills")

app = graph.compile()

png_data = app.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_data))
image.show()

answer = app.invoke({'name' : "Linda", 'age' : 23, 'skills' : "Python, Machine Learning, LangGraph, and AI Agents"})
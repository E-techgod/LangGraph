from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    values : List[int]
    name : str
    result : str
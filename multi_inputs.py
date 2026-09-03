import stat
from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    values : List[int]
    name : str
    result : str

def process_values(state : AgentState) -> AgentState:
    """ This pocess hanldes multiple different inputs """
    
    return {'result': f"Hi there {state['name']}! Your sum = {sum(state['values'])}"}
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    num1 : int
    num2: int
    operation : str
    finalNum : int 

def adder(state : AgentState) -> AgentState:
    """This node adds 2 nums"""
    return {'finalNum' : state['num1'] + state['num2']}

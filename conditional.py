import stat
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

def substraction(state : AgentState) -> AgentState:
    """This node adds 2 nums"""
    return {'finalNum' : state['num1'] - state['num2']}

def decide_next_node(state : AgentState) -> AgentState:
    """This node will select the next phase of the graph"""

    if state['operation'] == "+":
        return "add_operation"
    elif state['operation'] == "-":
        return "sub_operation"

    
import math
from typing import Dict, TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict): # 1. AgentState
    vals : List[int]
    name : str
    op : str
    result : str

def add_or_multiply(state : AgentState) -> AgentState: # 2. Create node
    """ This function will take the name and numbers as input
        If * nums will get multiply 
        If + nums will get add
    """
    if state['op'] == '+':
        ans = sum(state['vals'])
    elif state['op'] == '*':
        ans = math.prod((state['vals']))
    else: 
        None

    return {"result" :  f"Hi {state['name']}, your answer is: {ans}"}

graph = StateGraph(AgentState) # 3. Create graph

graph.add_node("conditional", add_or_multiply) # 4. Add node 

graph.set_entry_point("conditional") # 5. Add start
graph.set_finish_point("conditional") # 6. Add end 

app = graph.compile() # 7. Compie graph 

answer = app.invoke({'vals': [1,2,3,4], 'name': "Jack Sparrow", 'op': "+"}) # 8. Run app

print(answer['result'])


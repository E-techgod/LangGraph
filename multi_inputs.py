from socket import gaierror
import stat
from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict): # Create a state
    values : List[int]
    name : str
    result : str

def process_values(state : AgentState) -> AgentState: # Create a node
    """ This pocess hanldes multiple different inputs """
    print(state)
    return {'result': f"Hi there {state['name']}! Your sum = {sum(state['values'])}"}

graph = StateGraph(AgentState) # Start a graph

graph.add_node("processor", process_values) # Add a node
graph.set_entry_point("processor") # Add start
graph.set_finish_point("processor") # Add end

app = graph.compile() # Compile graph 

answers = app.invoke({'values' : [1,2,3,4], 'name' : 'Sancho'})

print(answers['result'])
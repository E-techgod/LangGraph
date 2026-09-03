from typing import Dict, TypedDict
from langgraph.graph import StateGraph

"""
1. Create class for graph with an agent
2. Create node for graph 
    Input: State -> Output: State 
3. Instantiate graph
4. Add node to graph
5. Create start graph
6. Create end graph 
7. Compile graph
8. Run graph 
"""

class AgentState(TypedDict): 
    name : str 

def compliment(state : AgentState) -> AgentState:
    """ This agent will compliment the user for learning"""
    return {'name': state['name'] + ", you are doing an amazing job learning LangGraph"}

graph = StateGraph(AgentState)

graph.add_node("compliment", compliment)

graph.set_entry_point("compliment")

graph.set_finish_point("compliment")

app = graph.compile()

result = app.invoke({"name" : "Elias"})

print(result["name"])
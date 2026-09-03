from typing import Dict, TypedDict
from langgraph.graph import StateGraph 

# Create the AgentState 
class AgentState(TypedDict): # Our State Schema
    message : str

# Create our first Node
# Input: State 
# Output: State
# Key habit, docstrings -> Tells the AI Agents what the function does
def greeting_node(state: AgentState) -> AgentState:
    """ Simple nodes that adds a greetings message to the state"""
    state['message'] = "Hey " + state['message'] + ", how is your day doing?"

    return state

############## GRAPH ############
# Start -> Node -> End

# Create our fist graph 
graph = StateGraph(AgentState)

# Add a node to the graph
graph.add_node("greeter", greeting_node)

# Add a start 
graph.set_entry_point("greeter")

# Add a end
graph.set_finish_point("greeter")

app = graph.compile()

# Display the graph 
from IPython.display import Image, display
display(Image(app.get_graph().draw_mermaid_png()))

result = app.invoke({"message": "Bob"}) # To run it

print(result["message"])
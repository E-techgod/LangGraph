import io
import random
from PIL import Image
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    name : str
    randNums : List[int]
    counter : int

def greeting_node(state : AgentState) -> AgentState: 
    """ This function will greet the user """
    return {
        'name' : f"Hi there, {state['name']}!",
        'counter' : state['counter'] == 0
    }

def random_num_node(state : AgentState) ->AgentState:
    """ This will generate random numbers from 0-10 """
    return{
        'randNum' : state['randNums'] + [random.randint(0,10)],
        'counter' : state["counter"] + 1
    }

def should_continue(state : AgentState) -> AgentState:
    """ This will determine if graph should continue or not """
    if state['counter'] < 5:
        print("ENTERING LOOP, " , state['counter'])
        return "loop" # Continue looping
    else:
        return "exit" # Exit loop 

# Order of this graph: greeting -> random -> random -> random -> random -> random -> exit

graph = StateGraph(AgentState)

graph.add_node("greet", greeting_node)
graph.add_node("random", random_num_node)
graph.add_edge("greet", "random")

graph.add_conditional_edges(
    "random", should_continue, # Source Node, Routing function
    {
        "loop" : "random", # Loops back to itself
        "exit" : END # End the graph
    }
)

graph.set_entry_point("greet")

app = graph.compile()

png_data = app.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_data))
image.show()

answer = app.invoke({'name' : "Elias", 'randNums': [], 'counter' : -100000000})

print(answer)
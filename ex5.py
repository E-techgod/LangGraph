import io
import random
from PIL import Image
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    name : str
    guesses : List[int]
    attempts : int
    target : int
    hint : int
    lower_bound : int
    upper_bound : int

def setup_node(state : AgentState) -> AgentState:
    """ This will start the game and assign a target num"""
    return {
        'name' : f"Hey there, {state['name']}! Lets begin the game!",
        'target' : random.randint(1,21),
        'guesses' : [],
        'attempts' : 0,
        'hint' : "Game started! Try to guess the number.",
        'lower_bound' : 1,
        'upper_bound' : 20,
    } 

def guess_node(state: AgentState) -> AgentState:
    """Generate a smarter guess based on previous hints"""
    
    possible_guesses = [i for i in range(state["lower_bound"], state["upper_bound"] + 1) if i not in state["guesses"]]
    if possible_guesses:
        guess = random.choice(possible_guesses)
    else:
        
        guess = random.randint(state["lower_bound"], state["upper_bound"])
    
    state["guesses"].append(guess)
    state["attempts"] += 1
    print(f"Attempt {state['attempts']}: Guessing {guess} (Current range: {state['lower_bound']}-{state['upper_bound']})")
    return state
    

def hint_node(state: AgentState) -> AgentState:
    """Here we provide a hint based on the last guess and update the bounds"""
    latest_guess = state["guesses"][-1]
    target = state["target"]
    
    if latest_guess < target:
        state["hint"] = f"The number {latest_guess} is too low. Try higher!"
        
        state["lower_bound"] = max(state["lower_bound"], latest_guess + 1)
        print(f"Hint: {state['hint']}")
        
    elif latest_guess > target:
        state["hint"] = f"The number {latest_guess} is too high. Try lower!"
      
        state["upper_bound"] = min(state["upper_bound"], latest_guess - 1)
        print(f"Hint: {state['hint']}")
    else:
        state["hint"] = f"Correct! You found the number {target} in {state['attempts']} attempts."
        print(f"Success! {state['hint']}")
    
    return state

def should_continue(state : AgentState) -> AgentState:
    """ This will determine if graph should continue or not """
    if state['attempts'] < 7: 
        print("ENTERING LOOP: ", state['attempts'])
        return "loop" # Continue looping
    else: 
        return "exit" # Exit loop

graph = StateGraph(AgentState)

graph.add_node("setup", setup_node)
graph.add_node("guess", guess_node)
graph.add_node("hint", hint_node)

graph.add_edge("setup", "guess")
graph.add_edge("guess", "hint")

graph.add_conditional_edges(
    "hint", should_continue, 
    {
        "loop" : "guess",
        "exit": END 
    }
)

graph.set_entry_point("setup")

app = graph.compile()

png_data = app.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(png_data))
image.show()

app.invoke({'name' : "Elias", 'guesses' : [], 'attempts' : 0, 'lower_bound' : 1, 'upper_bound' : 20})

    

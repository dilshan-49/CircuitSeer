from typing import TypedDict, Annotated, List
import operator

from langgraph.graph import StateGraph, END

# Import the specialist tools from your tools.py file
from agent import tools

# --- 1. Define the State of the Graph ---
# The state is the memory of your agent. It's a dictionary that gets passed
# between nodes, and each node can read from or write to it.

class AgentState(TypedDict):
    image_path: str  # The path to the image being analyzed
    component_type: str  # The identified type of the component (e.g., 'Resistor')
    raw_analysis: str # The raw analysis result from the vision model
    analysis_result: str # The final, detailed analysis from the specialist tool
    error: str # To hold any error messages

# --- 2. Define the Nodes of the Graph ---
# Each node is a function that performs an action. It takes the current state
# as input and returns a dictionary with the values to update in the state.

def identification_node(state: AgentState):
    print("---NODE: IDENTIFYING COMPONENT---")
    image_path = state.get("image_path")
    component_type_result = tools.identify_component(image_path)
    
    if component_type_result.startswith("API_ERROR:"):
        print(f"Error during identification: {component_type_result}")
        return {"error": component_type_result}

    cleaned_type = component_type_result.strip().replace("'", "").replace(".", "")
    print(f"Identified component type: {cleaned_type}")
    return {"component_type": cleaned_type}

def analysis_node(state: AgentState):
    """
    Second node: Takes the component type and calls the correct specialist tool.
    """
    print("---NODE: ANALYZING COMPONENT---")
    image_path = state.get("image_path")
    component_type = state.get("component_type", "").lower()

    analysis_result = ""
    # Route to the correct analysis tool based on the component type
    if "resistor" in component_type:
        analysis_result = tools.analyze_resistor(image_path)
    elif "capacitor" in component_type:
        analysis_result = tools.analyze_capacitor(image_path)
    elif "ic" in component_type or "integrated circuit" in component_type:
        analysis_result = tools.analyze_ic(image_path)
    else: # Fallback for Diodes, Transistors, LEDs, etc.
        analysis_result = tools.analyze_generic_component(image_path)
        
    return {"raw_analysis": analysis_result}

def summarization_node(state: AgentState):
    """NEW NODE: Takes the raw analysis and creates a user-friendly summary."""
    print("---NODE: SUMMARIZING ANALYSIS---")
    raw_analysis = state.get("raw_analysis")

    if not raw_analysis:
        error_msg = "Error: Raw analysis was not found in the agent's state. Cannot proceed with summarization."
        print(error_msg)
        return {"analysis_result": error_msg}

    if raw_analysis.startswith("API_ERROR:"):
        # If the analysis failed, pass the error through
        return {"analysis_result": raw_analysis}

    # If we have a valid raw analysis, summarize it
    summary = tools.summarize_analysis(raw_analysis)
    return {"analysis_result": summary}

def error_node(state: AgentState):
    """
    Error node: Handles any errors that occur.
    """
    print("---NODE: ERROR---")
    error = state.get("error")
    print(f"An error occurred: {error}")
    return {"analysis_result": f"Failed to process the image due to an error: {error}"}


# --- 3. Define the Conditional Edges ---
# This function decides which node to go to next based on the current state.

def router(state: AgentState):
    """
    The router function that directs the flow of the graph.
    """
    print("---ROUTER: DECIDING NEXT STEP---")
    if state.get("error"):
        print("Routing to: ERROR")
        return "error"
    
    component_type = state.get("component_type")
    if component_type and "error" not in component_type.lower():
        print(f"Component identified. Routing to: ANALYSIS")
        return "analyze"
    else:
        print("Could not identify component. Routing to: ERROR")
        return "error"

# --- 4. Assemble the Graph ---

def create_graph():
    """
    Creates and compiles the LangGraph agent.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("identifier", identification_node)
    workflow.add_node("analyzer", analysis_node)
    workflow.add_node("error_handler", error_node)
    workflow.add_node("summarizer", summarization_node)
    
    # Set the entry point of the graph
    workflow.set_entry_point("identifier")

    # Add the conditional edges
    workflow.add_conditional_edges("identifier", router, {"analyze": "analyzer", "error": "error_handler"})


    # Add the final edges
    workflow.add_edge("analyzer", "summarizer")
    workflow.add_edge("summarizer", END)
    workflow.add_edge("error_handler", END)

    # Compile the graph into a runnable app
    app = workflow.compile()
    print("Graph compiled successfully!")
    return app


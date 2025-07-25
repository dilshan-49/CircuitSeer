import os
import base64
from dotenv import load_dotenv
from typing import Optional
import json 

# LangChain and Google Gemini Imports
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# --- 1. Pydantic Models for Structured Output ---
# We define the exact JSON structure we want for each component type.



# --- 2. Configuration and Model Initialization ---

load_dotenv()
api_base = os.environ.get("DO_API_BASE")
do_api_key = os.environ.get("DO_API_KEY")
gemini_api_key = os.environ.get("GOOGLE_API_KEY")
chat_model = os.environ.get("DO_CHAT_MODEL")

if not all([api_base, do_api_key, gemini_api_key, chat_model]):
    raise ValueError("One or more DigitalOcean environment variables are missing.")


try:
    # Initialize Vision Model
    vlm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=gemini_api_key
    )
    
    # And a second instance configured for structured output
    print("Vision Model initialized successfully.")

    chat_llm = ChatOpenAI(model=chat_model, 
                          api_key=do_api_key, 
                          base_url=api_base,
                          temperature=0.5)
    print(f"Chat Model {chat_model} initialized successfully.")

except Exception as e:
    vlm, chat_llm = None, None, None
    print(f"Error initializing models: {e}")


# --- 3. Core Helper Functions ---
def _image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None

def _invoke_vision_model(prompt, base64_image):
    """Invokes the vision model"""
    if not vlm:
        return {"error": "Vision model is not available."}
    
    if not base64_image:
        return {"error": "Could not process image."}

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    try:
        print("Invoking vision model...")
        response = vlm.invoke([message])
        
        # --- DEBUGGING: Print the raw response from the API ---
        print(f"--- RAW API RESPONSE ---")
        print(f"Type: {type(response)}")
        print(f"Response Object: {response}")
        print(f"------------------------")
        
        # If it's a normal string, return it directly
        return response.content

    except Exception as e:
        print(f"An API error occurred: {e}")
        return f"API_ERROR: An error occurred while contacting the vision model. Details: {e}"


# --- 4. Specialist Analysis Tools (Updated to return JSON) ---

def identify_component(image_path):
    """Identifies the general component type (returns a simple string)."""
    base64_image = _image_to_base64(image_path)
    prompt = "Analyze the electronic component in this image. Respond with only a single-word category from this list: 'Resistor', 'Capacitor', 'IC', 'Transistor', 'Diode', 'LED', 'PCB', 'Other'."
    return _invoke_vision_model(prompt, base64_image)

def analyze_resistor(image_path):
    """Analyzes a resistor and returns a structured JSON object."""
    base64_image = _image_to_base64(image_path)
    prompt = """
    You are an expert electronics technician providing a quick summary for a colleague.
    Analyze the resistor and provide ONLY its key specifications with a single sentence mentioning the type of component. Do not add extra descriptions or recommendations.
    Format your response using Markdown bullet points.
    """
    return _invoke_vision_model(prompt, base64_image)

def analyze_capacitor(image_path):
    """Analyzes a capacitor and returns a structured JSON object."""
    base64_image = _image_to_base64(image_path)
    prompt = """
    You are an expert electronics technician providing a quick summary for a colleague.
    Analyze the capacitor in the image. Identify its type (e.g., Ceramic, Electrolytic), form (THT/SMD), capacitance, voltage rating etc.
    
    Provide ONLY these key specifications in a Markdown bulleted list with a single sentence mentioning the type of component. Do not add extra paragraphs about case style, applications, or polarity unless it's a direct marking.
    """
    return _invoke_vision_model(prompt, base64_image)

def analyze_ic(image_path):
    """Analyzes an IC and returns a structured JSON object."""
    base64_image = _image_to_base64(image_path)
    prompt = """
    You are an expert electronics technician providing a quick summary for a colleague.
    Analyze the Integrated Circuit (IC). Identify the primary part number and the manufacturer and other specs based on the image.
    
    Provide these key details in a Markdown bulleted list along with a single sentence mentioning the type of component.
    keep your response concise and focused on the IC's key specifications and short as possible.
    """
    return _invoke_vision_model(prompt, base64_image)

def analyze_generic_component(image_path):
    """Analyzes a generic component and returns a structured JSON object."""
    base64_image = _image_to_base64(image_path)
    prompt = """
    You are an expert electronics technician providing a quick summary for a colleague.
    Identify the component's most likely type (e.g., Diode, Transistor) and list its key markings or part numbers.
    
    Be brief and use a Markdown bulleted list.
    """
    return _invoke_vision_model(prompt, base64_image)



# --- 5. Chat Continuation Tool ---

def continue_chat(chat_history: list):
    """
    TOOL 6: Takes the existing chat history and generates the next AI response.
    """
    if not chat_llm:
        return "Error: Chat model is not available."
    
    # The first message from the AI is the initial, detailed analysis.
    # We use this as the context for all future questions.
    initial_analysis = chat_history[0][1]
    
    # We construct a message list for the LLM
    messages = [
        SystemMessage(content=f"You are an expert electronics assistant. You have already performed an analysis of a component with the following result: '{initial_analysis}'. Now, answer the user's follow-up questions based on this analysis and your general knowledge. Keep your answers concise and helpful."),
    ]

    # Add the rest of the history, converting our simple tuple format to LangChain messages
    for role, content in chat_history[1:]:
        if role == "human":
            messages.append(HumanMessage(content=content))
        elif role == "ai":
            messages.append(AIMessage(content=content))

    # Invoke the model with the full conversation history
    try:
        response = chat_llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"An error occurred during chat: {e}")
        return "Sorry, I encountered an error while processing your request."

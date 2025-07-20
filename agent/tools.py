import os
import base64
from dotenv import load_dotenv

# LangChain and Google Gemini Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- 1. Configuration and API Key Setup ---
load_dotenv()
google_api_key = os.environ.get("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")

# --- 2. Core Helper Functions ---
def _image_to_base64(image_path):
    """Converts an image file to a Base64 encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None

def _invoke_vision_model(prompt, base64_image):
    """A generic function to invoke the Gemini vision model with a prompt and image."""
    if not base64_image:
        return "Error: Could not process image."
        
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            },
        ]
    )
    print(f"Invoking model with prompt: '{prompt[:40]}...'")
    try:
        response = llm.invoke([message])
        print("Response received.")
        return response.content
    except Exception as e:
        print(f"An error occurred while calling the LLM API: {e}")
        return "Error: Failed to get a response from the vision model."

# --- 3. Specialist Analysis Tools (with Updated Prompts) ---

def identify_component(image_path):
    """
    TOOL 1: Identifies the general type of the component.
    """
    base64_image = _image_to_base64(image_path)
    prompt = "Analyze the electronic component in this image. Respond with only a single-word category from this list: 'Resistor', 'Capacitor', 'IC', 'Transistor', 'Diode', 'LED', 'PCB', 'Other'."
    return _invoke_vision_model(prompt, base64_image)

def analyze_resistor(image_path):
    """
    TOOL 2: Analyzes a resistor, considering both THT and SMD types.
    """
    base64_image = _image_to_base64(image_path)
    prompt = """
    Analyze the resistor in the image, considering it could be a Through-Hole (THT) or Surface-Mount (SMD) type.

    - If it is a THT resistor (cylindrical with wires): Analyze its color bands from left to right to determine its resistance and tolerance. Also, based on its physical size, estimate its power rating (e.g., 1/4W, 1/2W, 1W).
    - If it is an SMD resistor (small, rectangular chip): Read the numerical code printed on it (e.g., '103', '4R7') and calculate its resistance value. Explain the calculation (e.g., '103' is 10 x 10^3 ohms = 10kΩ).

    Present the final analysis clearly, stating the determined type (THT or SMD) and its specifications.
    """
    return _invoke_vision_model(prompt, base64_image)

def analyze_capacitor(image_path):
    """
    TOOL 3: Analyzes a capacitor, considering both THT and SMD types.
    """
    base64_image = _image_to_base64(image_path)
    prompt = """
    Analyze the capacitor in the image, considering it could be a Through-Hole (THT) or Surface-Mount (SMD) type.

    - If it is a THT capacitor (e.g., electrolytic, ceramic disc): Read the text on its body to find its capacitance (e.g., in µF, nF, or pF) and its maximum voltage rating (V).
    - If it is an SMD capacitor (small, rectangular, usually brown/gray): Look for a numerical code (e.g., '104'). If present, interpret this code to determine its capacitance. Explain the calculation (e.g., '104' is 10 x 10^4 pF = 100nF). Note that many SMD capacitors are unmarked; if so, state that.

    Present the final analysis clearly, stating the determined type (THT or SMD) and its specifications.
    """
    return _invoke_vision_model(prompt, base64_image)

def analyze_ic(image_path):
    """
    TOOL 4: Analyzes an Integrated Circuit (IC) to find its model number.
    """
    base64_image = _image_to_base64(image_path)
    prompt = "This is an Integrated Circuit (IC). Read all the text printed on its surface. Identify the primary model number, any secondary numbers (like date codes or batch numbers), and the manufacturer if possible."
    return _invoke_vision_model(prompt, base64_image)

def analyze_generic_component(image_path):
    """
    TOOL 5: A fallback for other components like diodes, transistors, etc.
    """
    base64_image = _image_to_base64(image_path)
    prompt = "Describe this electronic component, noting if it appears to be THT or SMD. Identify any markings, part numbers, or symbols on it and explain what they likely mean. For diodes, identify the cathode band. For transistors, identify any part numbers."
    return _invoke_vision_model(prompt, base64_image)

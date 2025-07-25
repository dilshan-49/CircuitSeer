import os
from dotenv import load_dotenv

# We will use the official OpenAI library for this utility
from openai import OpenAI, APIConnectionError

def list_available_models():
    """
    Connects to the DigitalOcean serverless inference endpoint and lists
    all available models.
    """
    print("--- Listing Available Models from DigitalOcean ---")

    # --- 1. Load Configuration from .env file ---
    load_dotenv()
    api_base = os.environ.get("DO_API_BASE")
    api_key = os.environ.get("DO_API_KEY")

    if not all([api_base, api_key]):
        print("\nERROR: Make sure DO_API_BASE and DO_API_KEY are set in your .env file.")
        return

    print(f"Connecting to endpoint: {api_base}\n")

    # --- 2. Initialize the OpenAI Client ---
    try:
        client = OpenAI(
            base_url=api_base,
            api_key=api_key,
        )
        print("Client initialized successfully.")
    except Exception as e:
        print(f"ERROR: Failed to initialize the OpenAI client.\nDetails: {e}")
        return

    # --- 3. Fetch and Print the List of Models ---
    try:
        print("Fetching model list...")
        models = client.models.list()
        
        print("\n--- Available Models ---")
        if not models.data:
            print("No models found.")
        else:
            for model in sorted(models.data, key=lambda x: x.id):
                print(f"- {model.id}")
        print("------------------------")

    except APIConnectionError as e:
        print(f"\n--- TEST FAILED ---")
        print(f"Could not connect to the server. Please check your DO_API_BASE URL.")
        print(f"Details: {e.__cause__}")
        print("---------------------")
    except Exception as e:
        print(f"\n--- TEST FAILED ---")
        print(f"An error occurred during the API call. Please check your DO_API_KEY.")
        print(f"Details: {e}")
        print("---------------------")


if __name__ == "__main__":
    list_available_models()

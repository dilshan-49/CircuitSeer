import os
import base64
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import the graph creation function from your agent code
from agent.graph import create_graph

# --- 1. Initialize Flask App and CORS ---
# CORS is needed to allow the browser (on a different port) to talk to this server.
app = Flask(__name__)
CORS(app)

# This is our simple in-memory session storage.
# In a production app, you'd use a database like Redis.
# Format: { "session_id": chat_history_list }
sessions = {}

# --- 2. Create a single instance of the LangGraph agent ---
# We create it once when the server starts so it's ready to go.
try:
    langgraph_app = create_graph()
    print("Agent created successfully.")
except Exception as e:
    print(f"FATAL: Could not create Agent. Error: {e}")
    langgraph_app = None

# --- 3. Define the API Endpoint ---
@app.route('/analyze', methods=['POST'])
def analyze_image_endpoint():
    """
    This function is called when the frontend sends an image for analysis.
    """
    if not langgraph_app:
        return jsonify({"error": "Agent is not available."}), 500

    print("Received request at /analyze endpoint.")
    
    # Get the image data from the request
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "No image data provided."}), 400

    image_data = base64.b64decode(data['image'])
    
    # Save the image to a temporary file
    # Using a unique filename to avoid conflicts
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    image_filename = os.path.join(temp_dir, f"{uuid.uuid4()}.jpg")
    
    try:
        with open(image_filename, 'wb') as f:
            f.write(image_data)
        print(f"Image saved temporarily to {image_filename}")

        # --- 4. Run the LangGraph Agent ---
        # The initial state for the graph requires the image path
        initial_state = {"image_path": image_filename, "chat_history":[]}
        
        # Invoke the agent with the initial state
        final_state = langgraph_app.invoke(initial_state)
        
        # Extract the final analysis result from the agent's state
        analysis = final_state.get("analysis_result", "No analysis result found.")
        

        # Create a new session
        session_id = str(uuid.uuid4())
        # Store the initial analysis as the first AI message in the chat history
        sessions[session_id] = [("ai", analysis)]
        
        print(f"New session created: {session_id}")
        return jsonify({"analysis": analysis, "session_id": session_id})

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Clean up the temporary image file
        if os.path.exists(image_filename):
            os.remove(image_filename)
            print(f"Cleaned up temporary file: {image_filename}")


@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    Endpoint to handle follow-up chat messages for an existing session.
    """
    data = request.get_json()
    session_id = data.get('session_id')
    user_message = data.get('message')

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid or missing session ID."}), 400
    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    # Retrieve the history and add the new user message
    chat_history = sessions[session_id]
    chat_history.append(("human", user_message))
    
    # We need to re-run the graph, but starting from the chat node.
    # For simplicity here, we'll just call a chat tool directly.
    # In a more complex graph, you would invoke a specific part of it.
    from agent.tools import continue_chat
    
    # The `continue_chat` tool needs the full history
    ai_response = continue_chat(chat_history)
    
    # Update the session history with the new AI response
    sessions[session_id].append(("ai", ai_response))
    
    print(f"Responded to chat in session: {session_id}")
    return jsonify({"response": ai_response})


# --- 5. Main Execution Block ---
if __name__ == '__main__':
    # Run the Flask server
    # host='0.0.0.0' makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)

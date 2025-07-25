import os
import base64
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
import traceback

from agent.graph import create_graph

app = Flask(__name__, static_folder='static', template_folder='templates')

# Initialize the agent once on startup
sessions = {}
langgraph_app = None

try:
    langgraph_app = create_graph()
except Exception as e:
    print(f"FATAL: Could not create LangGraph agent on startup. Error: {e}")
    traceback.print_exc()

# --- Route to serve the main UI ---
@app.route('/')
def index():
    """Serves the main index.html file."""
    return render_template('index.html')

# --- API Endpoints ---
@app.route('/analyze', methods=['POST'])
def analyze_image_endpoint():
    if not langgraph_app:
        return jsonify({"error": "Analysis agent is not available. Check server logs."}), 500

    if 'image' not in request.get_json():
        return jsonify({"error": "No image data provided in the request."}), 400
        
    image_data = base64.b64decode(request.get_json()['image'])
    
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    image_filename = os.path.join(temp_dir, f"{uuid.uuid4()}.jpg")
    
    try:
        with open(image_filename, 'wb') as f:
            f.write(image_data)

        initial_state = {"image_path": image_filename}
        final_state = langgraph_app.invoke(initial_state)
        
        raw_analysis = final_state.get("raw_analysis", "No detailed analysis was generated.")
        summarized_analysis = final_state.get("analysis_result", "Error: No summary was generated.")
        
        if "API_ERROR" in summarized_analysis or "Analysis Failed" in summarized_analysis:
            return jsonify({"error": summarized_analysis}), 500

        session_id = str(uuid.uuid4())
        sessions[session_id] = [("ai", raw_analysis)]
        sessions[session_id].append(("ai", summarized_analysis))
        
        return jsonify({"analysis": summarized_analysis, "session_id": session_id})

    except Exception as e:
        print("--- UNHANDLED EXCEPTION IN /analyze ---")
        traceback.print_exc()
        print("------------------------------------")
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500
    finally:
        if os.path.exists(image_filename):
            os.remove(image_filename)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    session_id, user_message = data.get('session_id'), data.get('message')
    if not all([session_id, user_message]) or session_id not in sessions:
        return jsonify({"error": "Invalid request. Missing session_id or message."}), 400
    
    chat_history = sessions[session_id]
    chat_history.append(("human", user_message))
    
    from agent.tools import continue_chat
    ai_response = continue_chat(chat_history)
    
    sessions[session_id].append(("ai", ai_response))
    return jsonify({"response": ai_response})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Endpoint to shut down the server."""
    print("Shutdown request received. Terminating server.")
    # This is a bit of a trick to shut down a Flask server from a request
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        # For non-Werkzeug servers, we might need a more forceful exit
        os._exit(0)
    shutdown_func()
    return "Server is shutting down..."

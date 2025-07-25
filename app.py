import webview
import threading
import sys
from server import app # Import the Flask app instance from server.py

# --- Global variable to hold the pywebview window ---
window = None

def start_server():
    """
    Function to run the Flask server.
    We disable Flask's reloader to prevent issues with pywebview.
    """
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"Failed to start Flask server: {e}")

def on_closed():
    """
    A cleanup function to be called when the pywebview window is closed.
    """
    print("UI window closed. Shutting down server.")
    # The server runs in a daemon thread, so it will exit when the main thread exits.
    # No explicit shutdown call is needed if the thread is a daemon.

if __name__ == '__main__':
    # --- Start the Flask server in a background thread ---
    # Setting the thread as a daemon means it will automatically terminate
    # when the main program (the pywebview window) exits.
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print("Flask server started in a background thread.")

    # --- Create and start the pywebview window ---
    # This creates a native OS window that displays our web UI.
    try:
        window = webview.create_window(
            'CircuitSeer',
            'http://127.0.0.1:5000', # Load the Flask server's URL
            width=1200,
            height=800,
            resizable=True
        )
        window.events.closed += on_closed
        print("Starting UI window...")
        webview.start()
        print("CircuitSeer application has been shut down.")

    except Exception as e:
        print(f"Failed to create or start pywebview window: {e}")
    
    sys.exit()


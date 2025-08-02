import threading
import sys
import server_pi # Import the Pi-specific server
from utils.camera_pi import Camera # Import the Pi-specific camera class
import os

os.environ["WEBKIT_DISABLE_COMPOSITING_MODE"] = "1"

import webview

pi_camera = None

def start_server(camera_instance):
    """Function to run the Flask server, passing in the camera object."""
    try:
        server_pi.camera = camera_instance
        server_pi.app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"Failed to start Flask server: {e}")

if __name__ == '__main__':
    try:
        pi_camera = Camera()
        print("PiCamera initialized successfully.")

        server_thread = threading.Thread(target=start_server, args=(pi_camera,), daemon=True)
        server_thread.start()
        print("Flask server (Pi version) started in a background thread.")

        window = webview.create_window(
            'CircuitSeer (Raspberry Pi)',
            'http://127.0.0.1:5000', # Load the root URL, which serves index_pi.html
            width=1200,
            height=800,
            resizable=True
        )
        
        def on_closed():
            print("UI window closed. Releasing camera.")
            pi_camera.release()
        
        window.events.closed += on_closed
        
        webview.start()
        print("CircuitSeer application has been shut down.")

    except Exception as e:
        print(f"Failed to start application: {e}")
        if pi_camera:
            pi_camera.release()
    
    sys.exit()

import cv2
import threading
import time
from picamera2 import Picamera2

class Camera:
    """
    A class to manage the Raspberry Pi camera using the picamera2 library.
    It captures frames in a background thread for a smooth video stream.
    """
    def __init__(self):
        self.picam2 = Picamera2()
        # Configure the camera for video streaming
        config = self.picam2.create_preview_configuration(main={"size": (640, 480),"format": "RGB888"})
        self.picam2.configure(config)
        
        self.picam2.start()
        # Allow the camera to warm up
        time.sleep(2.0)
        
        self.frame = None
        self.lock = threading.Lock()
        self.is_running = True
        
        # Start a background thread to continuously read frames
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        print("Raspberry Pi camera thread started using picamera2.")

    def _update(self):
        """Internal method to read frames from the camera."""
        while self.is_running:
            # capture_array() returns a NumPy array, which is compatible with OpenCV
            frame_array = self.picam2.capture_array()
            with self.lock:
                self.frame = frame_array
            time.sleep(0.03) # Limit to ~30 fps

    def get_frame(self):
        """Returns the latest captured frame as a NumPy array."""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def get_jpeg_frame(self):
        """Encodes the latest frame as a JPEG image."""
        frame = self.get_frame()
        if frame is not None:
            # We still use cv2 here for its highly efficient JPEG encoding
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                return jpeg.tobytes()
        return None

    def release(self):
        """Releases the camera resources."""
        self.is_running = False
        self.thread.join() # Wait for the thread to finish
        self.picam2.stop()
        print("Camera released.")

# --- Generator function for streaming ---
def generate_frames(camera):
    """A generator function that yields JPEG-encoded frames for video streaming."""
    while True:
        frame_bytes = camera.get_jpeg_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03)

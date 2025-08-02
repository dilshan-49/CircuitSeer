# Import the necessary libraries
import time
from picamera2 import Picamera2,Preview

print("Attempting to initialize the camera...")

try:
    # Create an instance of the Picamera2 object
    picam2 = Picamera2()


    # Start the camera preview
    # A preview window should appear on your Pi's desktop
    picam2.start_preview(Preview.QT, x=100, y=200, width=800, height=600)
    
    preview_config = picam2.create_preview_configuration()
    picam2.configure(preview_config)

    picam2.start()
    
    print("Camera initialized successfully! A preview window should be visible for 5 seconds.")
    
    # Keep the preview open for 5 seconds
    time.sleep(5)

    print("Closing camera.")

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure the camera is connected properly and enabled in raspi-config.")

finally:
    # Always make sure to stop the camera
    if 'picam2' in locals() and picam2.is_open:
        
        picam2.stop()
        print("Camera stopped.")
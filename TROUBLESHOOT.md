# Troubleshooting Guide for CircuitSeer on Raspberry Pi

This guide covers common setup and runtime issues you might encounter, when setting up the application on Raspberry Pi.

---

### `ModuleNotFoundError: No module named 'picamera2'`

**Symptom:**
After activating your virtual environment (`venv`) and installing requirements, you run `app_pi.py` and get an error that the `picamera2` module cannot be found, even though you installed it with `sudo apt install`.

**Cause:**
Standard virtual environments are isolated from the system's Python packages. The `picamera2` library is installed globally via `apt`, so your isolated `venv` cannot see it.

**Solution:**
You must create the virtual environment with the `--system-site-packages` flag. This allows the `venv` to access globally installed system libraries like `picamera2`.

1.  Deactivate and delete your old `venv` folder.
2.  Recreate it with the correct flag:
    ```bash
    python3 -m venv venv --system-site-packages
    ```
3.  Activate the new environment and reinstall your project's dependencies:
    ```bash
    source venv/bin/activate
    pip install -r requirements.txt
    ```

---

### `ValueError: numpy.dtype size changed, may indicate binary incompatibility`

**Symptom:**
When running the camera test script or the main application, the program crashes with a `ValueError` related to a `numpy.dtype` size mismatch.

**Cause:**
This is a binary incompatibility issue. The system-installed `picamera2` and its dependency `simplejpeg` were compiled against a different version of NumPy than the one `pip` installed in your virtual environment.

**Solution:**
Force-reinstall `simplejpeg` using `pip` inside your activated virtual environment. This will compile it against the version of NumPy that is currently installed in your `venv`.

```bash
# Make sure your venv is active
pip install --force-reinstall --no-cache-dir simplejpeg
```
*Note: In some cases, reinstalling `numpy` first can also help: `pip install --force-reinstall --no-cache-dir numpy`.*

---

### `pywebview` Fails to Start on Raspberry Pi

**Symptom:**
When running `app_pi.py`, the script crashes with an error like `ValueError: Namespace WebKit2 not available` or `No module named 'qtpy'`.

**Cause:**
`pywebview` requires a GUI toolkit (like GTK or Qt) to be installed on the system, along with the corresponding Python bindings. These are often missing from a fresh Raspberry Pi OS installation.

**Solution:**
Install the necessary system libraries for GTK and the Python bindings for it.

1.  Install the system dependencies (no `venv` needed):
    ```bash
    sudo apt-get update
    sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.0-dev
    ```
2.  Install the Python bindings inside your activated `venv`:
    ```bash
    pip install PyGObject
    ```

---

### UI Window is Garbled or Glitched on Raspberry Pi

**Symptom:**
The application window opens, but the UI is a mess of glitched lines and colors, making it unusable. This is most common when running over a VNC connection.

**Cause:**
This is a graphics rendering issue. `pywebview` is trying to use hardware (GPU) acceleration, which is not compatible with the VNC session's software-based screen sharing.

**Solution:**
The `app_pi.py` script includes a fix for this. It sets an environment variable to force software rendering *before* `pywebview` is imported. If you encounter this issue, ensure these lines are at the very top of your `app_pi.py` file:

```python
import os
# This environment variable MUST be set BEFORE importing pywebview.
os.environ["WEBKIT_DISABLE_COMPOSITING_MODE"] = "1"

import webview
# ... rest of the script
```

# CircuitSeer: AI Visual Inspection Agent

![CircuitSeer Banner](https://placehold.co/1200x300/020617/7c3aed?text=CircuitSeer&font=inter)

CircuitSeer is an intelligent agent designed to assist electronics engineers and hobbyists by automating the identification and analysis of electronic components. Using a simple web interface and the power of large language models, you can capture or upload an image of a component, and CircuitSeer will provide a detailed analysis of its specifications.

This project leverages the LangGraph framework to create a stateful, multi-step agent that can reason about what it sees and decide which specialized tool to use for analysis.

---

## ✨ Features

- **Component Identification**: Automatically identifies the type of component (Resistor, Capacitor, IC, etc.).
- **THT & SMD Analysis**: Intelligently handles both Through-Hole and Surface-Mount components.
  - **Resistors**: Reads color codes (THT) or numerical codes (SMD) to determine resistance.
  - **Capacitors**: Reads printed values (THT) or 3-digit codes (SMD) to determine capacitance.
  - **ICs**: Identifies model numbers and manufacturers.
- **Web-Based UI**: An intuitive interface to capture images from a webcam or upload existing files.
- **Real-time Analysis**: Provides detailed analysis results directly in the browser.

---

## 🛠️ How It Works

The project uses a client-server architecture:

1. **Frontend (`index.html`)**: A single-page web application that captures/uploads an image and displays the results.
2. **Backend (`server.py`)**: A Flask web server that provides an API endpoint (`/analyze`). It receives the image from the frontend.
3. **AI Agent (`agent/graph.py`)**: The Flask server invokes a LangGraph agent. The agent first runs an `identification_node` to determine the component type.
4. **Router & Tools (`agent/tools.py`)**: Based on the component type, a router directs the agent to use a specialized analysis tool (e.g., `analyze_resistor`). This tool uses a tailored prompt to get detailed specs from the Google Gemini vision model.
5. **LLM API**: The agent communicates with the Google Gemini 1.5 Flash API to perform the visual analysis.

---

## 🚀 Technology Stack

- **Backend**: Python, Flask, LangChain, LangGraph
- **AI Model**: Google Gemini 1.5 Flash
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Core Libraries**: `opencv-python`, `python-dotenv`

---

## 📂 Project Structure

```bash
CircuitSeer/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py          # Defines the LangGraph agent structure
│   └── tools.py          # Contains specialist analysis functions (tools)
│
├── utils/
│   └── camera.py         # (Optional) For any advanced camera logic
│
├── temp_images/          # Temporary storage for images being analyzed
│
├── server.py             # The Flask backend server
├── index.html            # The frontend web interface
│
├── .env                  # Stores secret API keys
└── requirements.txt      # Project dependencies
```

---

## ⚙️ Setup and Installation

Follow these steps to get CircuitSeer running on your local machine.

### Prerequisites

- Python 3.8+
- A webcam (for live capture)
- A Google API Key with the Gemini API enabled.

### 1. Clone the Repository

```bash
git clone https://github.com/dilshan-49/CircuitSeer.git
cd CircuitSeer
```

### 2. Set Up Python Environment

It's recommended to use a virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages.

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Create a file named `.env` in the root of the project folder and add your Google API key:

```bash
GOOGLE_API_KEY="your_secret_google_api_key_here"
```

### 5. Run the Application

You need to run the backend server first.

```bash
python server.py
```

This will start the Flask server, typically on `http://127.0.0.1:5000`.

### 6. Launch the Frontend

Open the `index.html` file in your web browser (e.g., Chrome, Firefox). The application should now be running!

---

## 📖 Usage

1. **Open `index.html`** in your browser.
2. Allow the browser to access your camera.
3. **To use the camera**: Position a component in the camera's view and click **"Capture Image"**.
4. **To upload a file**: Click **"Upload Image"** and select an image file from your device.
5. On the confirmation screen, click **"Analyze Image"**.
6. Wait for the AI analysis to appear on the right side of the screen.
7. Click **"Start Over"** to analyze another component.

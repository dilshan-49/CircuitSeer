# CircuitSeer: AI Visual Inspection App

![CircuitSeer Banner](https://placehold.co/1200x300/020617/7c3aed?text=CircuitSeer&font=inter)

CircuitSeer is a standalone application designed to assist electronics engineers and hobbyists by automating the identification and analysis of electronic components. Using a clean, native UI, you can capture an image from a webcam or upload a file, and CircuitSeer will provide a detailed analysis and allow you to ask follow-up questions in a conversational chat.

This project leverages a sophisticated hybrid AI model approach and the LangGraph framework to create a stateful, multi-step agent that can reason about what it sees and decide which specialized tool to use for analysis and conversation.

---

## ✨ Features

- **Standalone Desktop Application**: Runs in its own native window without needing a web browser, providing a professional, focused experience.
- **Hybrid AI Backend**: Utilizes Google Gemini for robust, state-of-the-art vision analysis and a fast DigitalOcean model (e.g., openai-gpt-4o-mini) for responsive, high-quality conversational chat.
- **Component Identification**: Automatically identifies the type of component (Resistor, Capacitor, IC, etc.).
- **Detailed THT & SMD Analysis**: Intelligently handles both Through-Hole and Surface-Mount components with detailed, formatted output.
- **Conversational Follow-up**: Engage in a chat with the AI assistant to ask further questions about the analyzed component (e.g., "What are its common uses?", "Suggest an alternative.").
- **Dual Input Methods**: Analyze components using a live webcam feed or by uploading an existing image file.
- **Clean Shutdown**: A dedicated power button in the UI cleanly terminates both the frontend window and the backend server.

---

## 🛠️ How It Works

CircuitSeer is a unified desktop application built on a client-server architecture, wrapped in a native window.

1. **Application Wrapper (`app.py`)**: The main entry point. It uses `pywebview` to create a native desktop window. It also starts the Flask backend server in a separate, background thread.
2. **Frontend (`templates/index.html`)**: A single-page web application that runs inside the `pywebview` window. It handles the camera feed, image uploads, and all user interactions, communicating with the backend via local HTTP requests.
3. **Backend (`server.py`)**: A Flask web server that provides API endpoints (`/analyze`, `/chat`, `/shutdown`). It receives requests from the frontend and manages the AI agent's sessions.
4. **AI Agent (`agent/graph.py`)**: The Flask server invokes a LangGraph agent for each new analysis. The agent follows a defined workflow:
    - **Identification Node**: First, it uses the Gemini vision model to identify the component type.
    - **Analysis Node**: Based on the type, a router directs the agent to use a specialized analysis tool.
5. **AI Tools (`agent/tools.py`)**: These are the functions that interact with the AI models:
    - **Vision Tools**: Send the image and a detailed prompt to the **Google Gemini** API to get a comprehensive analysis.
    - **Chat Tool**: Sends the conversation history and a new user query to the **DigitalOcean** chat model API to get a context-aware response.

---

## 🚀 Technology Stack

- **Application Wrapper**: `pywebview`
- **Backend**: Python, Flask, LangChain, LangGraph
- **AI Models**:
  - **Vision**: Google Gemini 1.5 Flash (via `langchain-google-genai`)
  - **Chat**: DigitalOcean Serverless Inference (e.g., `openai-gpt-4o-mini` via `langchain-openai`)
- **Frontend**: HTML, Tailwind CSS, JavaScript, Showdown.js (for Markdown rendering)
- **Core Libraries**: `opencv-python`, `python-dotenv`

---

## 📂 Project Structure

```
CircuitSeer/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py          # Defines the LangGraph agent structure
│   └── tools.py          # Contains specialist analysis & chat tools
│
├── templates/
│   └── index.html        # The frontend web interface
│
├── temp_images/          # Temporary storage for images
│
├── app.py                # The main script to launch the application
├── server.py             # The Flask backend server
│
├── .env                  # Stores secret API keys
└── requirements.txt      # Project dependencies
```

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.8+
- A webcam (for live capture)
- A Google API Key with the Gemini API enabled.
- A DigitalOcean Model Access Key and API Base URL.

### 1. Clone the Repository

```bash
git clone https://github.com/dilshan-49/CircuitSeer.git
cd CircuitSeer
```

### 2. Set Up Python Environment & Install Dependencies

It's highly recommended to use a virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a file named `.env` in the root of the project folder and add your API keys:

```env
# --- Google Credentials (for Vision) ---
GOOGLE_API_KEY="your_google_api_key_here"

# --- DigitalOcean Credentials (for Chat) ---
DO_API_BASE="[https://inference.do-ai.run/v1](https://inference.do-ai.run/v1)"
DO_API_KEY="your_digitalocean_api_key"
DO_CHAT_MODEL="anthropic-claude-3.7-sonnet"
```

---

## ▶️ How to Run

To start the entire application (both the server and the UI), run the `app.py` script from your terminal:

```bash
python app.py
```

A native desktop window for CircuitSeer will open.

---

## 📖 Usage

1. **Capture or Upload**: Use the live camera feed and the **"Capture Image"** button, or click **"Upload Image"** to select a file from your computer.
2. **Confirm**: Review the captured image and click **"Analyze Image"**.
3. **Analyze**: The initial analysis from the AI will appear in the chat window on the right.
4. **Chat**: Use the input box at the bottom of the chat window to ask follow-up questions.
5. **Exit**: Click the red power icon in the top-right corner to cleanly shut down the application.

---

## 🔮 Potential Future Developments

I believe this project provides a solid foundation that can be extended in several exciting directions to create an even more powerful assistant. Some potential enhancements are:

- **RAG-Powered Knowledge Base**: To improve factual accuracy, a Retrieval-Augmented Generation (RAG) architecture could be implemented. This would involve creating a vector database from component datasheets(can use knowledgebase from the Digital Ocean services), allowing the agent to ground its answers in verifiable technical documentation.

- **E-commerce Sourcing Agent**: A new agent tool could be developed to search online electronics vendors (e.g., Digi-Key, Mouser). This would enable users to ask "Where can I buy this?" and receive a list of suppliers, prices, and direct product links.

- **Full PCB Analysis**: The agent's capabilities could be expanded to analyze an entire Printed Circuit Board (PCB). This would allow users to upload a photo of a board and ask the agent to identify multiple components, locate specific parts, or describe different sections of the circuit.

- **Project History & BOM Generation**: A feature could be added to save a history of all components analyzed for a specific project. From this history, the agent could be tasked with generating a complete Bill of Materials (BOM), including part numbers, specifications, and sourcing links.

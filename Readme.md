# **Speech-to-Text and Text-to-Speech Assistant**

Welcome to the **Speech-to-Text and Text-to-Speech Assistant**! This application leverages **React** for the frontend, **Flask** for the backend, and OpenAI's GPT for generating intelligent responses. The assistant converts your spoken queries into text, processes them using a powerful AI model, and responds audibly to create an interactive conversational experience.

---

![alt text](<frontend/src/assets/Screenshot 2024-11-27 225230.png>)

## **Features**

- 🎤 **Speech-to-Text**: Real-time audio transcription using OpenAI Whisper.
- 🧠 **AI-Powered Responses**: Intelligent query processing via OpenAI's GPT model.
- 🔊 **Text-to-Speech**: Converts responses into natural-sounding speech with `gTTS`.
- 💻 **User-Friendly Interface**: Built using React for a smooth and interactive experience.

---

## **Getting Started**

### **1. Prerequisites**

- **Node.js**: For running the React frontend.
- **Python 3.x**: For running the Flask backend.
- **Dependencies**:
  - Frontend: Installed via `npm`.
  - Backend: Installed via `pip`.

---

### **2. Installation**

#### **Clone the Repository**

```bash
git clone <repository-url>
cd <repository-folder>
```

#### **Frontend Setup**

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

#### **Backend Setup**

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python app.py
   ```

---

### **3. How to Use**

1. Open the application in your browser at [http://localhost:3000](http://localhost:3000).
2. Click the **"Record"** button and start speaking your query.
3. The assistant will transcribe your speech, process it, and speak back the response.

---

## **Architecture Overview**

This app consists of the following key components:

- **Frontend**: Built using React for user interaction.
- **Backend**: Flask-based Python backend for audio processing, AI interaction, and speech synthesis.
- **Speech-to-Text**: OpenAI Whisper for high-accuracy transcription.
- **LLM**: OpenAI GPT for dynamic query responses.
- **Text-to-Speech**: `gTTS` for converting text to audio responses.

---

## **Troubleshooting**

- Ensure both the frontend and backend servers are running.
- Check the microphone and audio playback settings on your device.
- If you encounter issues, refer to the log outputs from the terminal for debugging.

---

## **Contributing**

We welcome contributions! If you’d like to improve this project, feel free to fork the repository and submit a pull request.

---

## **More Information**

For a detailed walkthrough of the project, its architecture, and future improvements, please refer to the **[https://docs.google.com/presentation/d/17UKPttav2GZR-TxPyG7hNnxGE9t49ttK-uhu0n2j1Ms/edit?usp=sharing](#)**.

---

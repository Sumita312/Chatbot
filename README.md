# 🌸 Lumi —  AI Chatbot

Lumi is a beautiful AI-powered chatbot built with **Python**, **Streamlit**, and **Groq LLMs**. It combines an elegant user interface with conversational AI, voice input, user authentication, and persistent chat history.

## ✨ Features

* 🤖 AI-powered conversations using Groq's Llama 3.3 70B model
* 👤 User registration and login system
* 🔒 Secure password hashing
* 💬 Personal chat history for each user
* 🎙️ Voice-to-text input using speech recognition
* 🌸 Aesthetic and minimal user interface
* 📱 Responsive Streamlit web application
* 💾 Local storage of users and chat history

## 🛠️ Technologies Used

* Python
* Streamlit
* Groq API
* SpeechRecognition
* SoundDevice
* NumPy
* JSON Storage
* dotenv

## 📂 Project Structure

```text
Chatbot/
│
├── chatbot_gui.py      # Main application
├── .env               # API key (not uploaded)
├── .gitignore
├── README.md
├── users.json         # Generated locally
└── chats.json         # Generated locally
```

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/Sumita312/Chatbot.git
cd Chatbot
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create a .env file

```env
GROQ_API_KEY=your_api_key_here
```

## ▶️ Run the application

```bash
streamlit run chatbot_gui.py
```

## 🎙️ Voice Support

Lumi supports speech-to-text input. Click the microphone button and speak your message. The application will automatically convert your speech into text and send it to the chatbot.

## 🔐 Security

* Passwords are hashed using SHA-256.
* API keys are stored locally using environment variables.
* Sensitive files are excluded from Git tracking using `.gitignore`.

## 📸 Features Preview

* User authentication
* Personalized chat history
* Voice interaction
* Elegant aesthetic design
* Fast AI responses

## 🚀 Future Improvements

* Database integration (SQLite/PostgreSQL)
* Dark mode support
* Chat export functionality
* Conversation search
* Text-to-speech responses
* Cloud deployment

## 👩‍💻 Author

**Sumita312**

Built with ❤️ using Streamlit and Groq AI.

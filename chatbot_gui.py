from groq import Groq
from dotenv import load_dotenv
import os
import streamlit as st
import json
import hashlib
import sounddevice as sd
import numpy as np
import speech_recognition as sr

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── FILE PATHS ──────────────────────────────────────────
USERS_FILE = "users.json"
CHATS_FILE = "chats.json"


# ── HELPERS ─────────────────────────────────────────────
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    users = load_json(USERS_FILE)
    if username in users:
        return False
    users[username] = hash_password(password)
    save_json(USERS_FILE, users)
    return True


def login_user(username, password):
    users = load_json(USERS_FILE)
    return users.get(username) == hash_password(password)


def load_user_chats(username):
    chats = load_json(CHATS_FILE)
    return chats.get(username, [])


def save_user_chats(username, history):
    chats = load_json(CHATS_FILE)
    chats[username] = history
    save_json(CHATS_FILE, chats)


# ── GROQ ────────────────────────────────────────────────
def generate_response(query, history):
    messages = [
        {"role": "system", "content": "You are Lumi, a warm, friendly, aesthetic AI companion. Be concise, lovely, and supportive."}
    ]
    for h, a in history:
        messages.append({"role": "user", "content": h})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": query})
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"oops, something went wrong ♡  {e}"


# ── VOICE ───────────────────────────────────────────────
def voice_input():
    try:
        st.toast("🎙️ Listening... speak now!")
        duration = 5
        sample_rate = 16000
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        recognizer = sr.Recognizer()
        audio = sr.AudioData(audio_data.tobytes(), sample_rate, 2)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.warning("couldn't hear anything ♡")
        return ""
    except Exception as e:
        st.warning(f"Voice error: {e}")
        return ""


# ── PAGE CONFIG & CSS ────────────────────────────────────
st.set_page_config(page_title="lumi ✦", page_icon="🌸", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&family=Inter:wght@300;400;500&display=swap');

body, .stApp {
    background-color: #fdf6f0 !important;
}

.header {
    background: linear-gradient(135deg, #e8b4b8, #c8a5b0);
    padding: 28px 20px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(180,100,110,0.15);
}
.header h1 {
    color: #3d2020;
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-size: 2.4em;
    margin: 0;
    letter-spacing: 1px;
}
.header p {
    color: #6b3a3a;
    font-family: 'Inter', sans-serif;
    font-size: 0.9em;
    margin: 6px 0 0 0;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.auth-box {
    background: #fff8f5;
    border: 1px solid #f2d4d7;
    border-radius: 16px;
    padding: 30px;
    margin: 20px auto;
    max-width: 420px;
    box-shadow: 0 2px 16px rgba(180,100,110,0.08);
}
.auth-box h2 {
    color: #5c3d3d;
    font-family: Georgia, serif;
    font-style: italic;
    text-align: center;
    margin-bottom: 20px;
}

.stTextInput > div > div > input {
    background-color: #fff0ee !important;
    border: 1px solid #e8b4b8 !important;
    border-radius: 10px !important;
    color: #5c3d3d !important;
    font-family: 'Inter', sans-serif;
}

.stButton > button {
    background: linear-gradient(135deg, #e8b4b8, #d4919a) !important;
    color: #3d2020 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    width: 100%;
    padding: 10px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #d4919a, #b5636e) !important;
    color: white !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(180,100,110,0.3);
}

.sidebar-user {
    background: linear-gradient(135deg, #f2d4d7, #e8b4b8);
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    margin-bottom: 16px;
    color: #5c3d3d;
    font-family: Georgia, serif;
    font-style: italic;
}

/* Claude-style history items */
.hist-item {
    padding: 8px 10px;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    font-size: 0.85em;
    color: #5c3d3d;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background 0.15s;
    border: none;
    background: transparent;
    width: 100%;
    text-align: left;
    display: block;
    margin-bottom: 2px;
}
.hist-item:hover {
    background: #f2d4d7 !important;
}

div[data-testid="stChatMessage"] {
    background: transparent !important;
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ───────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""
if "selected_convo" not in st.session_state:
    st.session_state.selected_convo = None


# ── HEADER ──────────────────────────────────────────────
st.markdown("""
    <div class="header">
        <h1>✦ lumi</h1>
        <p>your aesthetic AI companion</p>
    </div>
""", unsafe_allow_html=True)


# ── AUTH SCREEN ─────────────────────────────────────────
if not st.session_state.logged_in:

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌸 Login"):
            st.session_state.auth_mode = "login"
    with col2:
        if st.button("✦ Register"):
            st.session_state.auth_mode = "register"

    st.markdown('<div class="auth-box">', unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        st.markdown("<h2>welcome back ♡</h2>", unsafe_allow_html=True)
        username = st.text_input("username", key="login_user")
        password = st.text_input("password", type="password", key="login_pass")
        if st.button("login ♡"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.history = load_user_chats(username)
                st.rerun()
            else:
                st.error("incorrect username or password ♡")

    else:
        st.markdown("<h2>create your account ✦</h2>", unsafe_allow_html=True)
        st.caption("password: min 5 characters + at least one special character (!@#$%^&* etc.)")
        username = st.text_input("choose a username", key="reg_user")
        password = st.text_input("choose a password", type="password", key="reg_pass")
        password2 = st.text_input("confirm password", type="password", key="reg_pass2")
        if st.button("register ♡"):
            if password != password2:
                st.error("passwords don't match ♡")
            elif len(password) < 5:
                st.error("password must be at least 5 characters ♡")
            elif not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
                st.error("password must contain at least one special character ♡")
            elif register_user(username, password):
                st.success("account created! please login ♡")
                st.session_state.auth_mode = "login"
                st.rerun()
            else:
                st.error("username already taken ♡")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ── SIDEBAR ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="sidebar-user">✦ {st.session_state.username}</div>', unsafe_allow_html=True)

    st.markdown("### ♡ chats")

    if st.session_state.history:
        for i, (h, a) in enumerate(st.session_state.history):
            preview = h[:32] + "..." if len(h) > 32 else h
            # render as plain clickable text like Claude's sidebar
            if st.markdown(
                f'<div class="hist-item" onclick="void(0)">💬 {preview}</div>',
                unsafe_allow_html=True
            ) is None:
                # use a hidden button to capture clicks
                pass
            if st.button(preview, key=f"hist_{i}", help="click to view full conversation",
                         use_container_width=True):
                st.session_state.selected_convo = i
                st.rerun()
    else:
        st.markdown("<small style='color:#b08080;'>no chats yet ♡</small>", unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ clear chat", use_container_width=True):
        st.session_state.history = []
        st.session_state.selected_convo = None
        save_user_chats(st.session_state.username, [])
        st.rerun()

    if st.button("🚪 logout", use_container_width=True):
        save_user_chats(st.session_state.username, st.session_state.history)
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.history = []
        st.session_state.selected_convo = None
        st.rerun()


# ── FULL CONVO VIEWER ────────────────────────────────────
if st.session_state.selected_convo is not None:
    idx = st.session_state.selected_convo
    if idx < len(st.session_state.history):
        st.markdown("### 💬 full conversation")
        for j, (hu, as_) in enumerate(st.session_state.history):
            with st.chat_message("user"):
                st.write(hu)
            with st.chat_message("assistant", avatar="🌸"):
                st.write(as_)
        st.divider()
        if st.button("✕ back to chat"):
            st.session_state.selected_convo = None
            st.rerun()
    st.stop()


# ── CHAT ────────────────────────────────────────────────
for human, assistant in st.session_state.history:
    with st.chat_message("user"):
        st.write(human)
    with st.chat_message("assistant", avatar="🌸"):
        st.write(assistant)


# ── INPUT ROW ───────────────────────────────────────────
col1, col2 = st.columns([9, 1])

with col2:
    if st.button("🎙️"):
        spoken = voice_input()
        if spoken:
            st.session_state.voice_text = spoken
            st.rerun()

query = st.chat_input("say something lovely...")

if st.session_state.voice_text:
    query = st.session_state.voice_text
    st.session_state.voice_text = ""

if query:
    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant", avatar="🌸"):
        reply = generate_response(query, st.session_state.history)
        st.write(reply)
    st.session_state.history.append((query, reply))
    save_user_chats(st.session_state.username, st.session_state.history)
    st.rerun()


# ── FOOTER ──────────────────────────────────────────────
st.markdown("<br><center><sub>made with ♡ lumi v2.0</sub></center>", unsafe_allow_html=True)
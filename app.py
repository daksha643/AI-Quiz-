import streamlit as st
import json
import os
import requests
import re
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict
from auth import AuthManager
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Quiz Master",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ SESSION STATE INITIALIZATION ============
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'api_status' not in st.session_state:
    st.session_state.api_status = "Checking API..."
    st.session_state.api_status_type = "warning"
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False

# ============ INITIALIZE AUTH MANAGER ============
auth_manager = AuthManager()


# ============ CSS ============

st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    
    /* ========== BACKGROUND ========== */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        background-attachment: fixed !important;
    }
    
    .stApp > header { background: transparent !important; }
    .stApp > div { background: transparent !important; }
    .main > div { background: transparent !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* ========== MAIN HEADER ========== */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-radius: 10px;
        color: white !important;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        color: white !important;
    }
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
    }
    
    /* ========== LOGIN PAGE ========== */
    .auth-container {
        background: rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 35px 30px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        box-shadow: 0 15px 50px rgba(0,0,0,0.25) !important;
        max-width: 420px !important;
        margin: 0 auto !important;
    }
    
    .auth-container h3 {
        color: white !important;
        text-align: center !important;
        font-weight: 600 !important;
    }
    
    .auth-container label {
        color: white !important;
        font-weight: 500 !important;
    }
    
    .auth-container input {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }
    
    .auth-container input::placeholder {
        color: rgba(255,255,255,0.5) !important;
    }
    
    .auth-container input:focus {
        border-color: rgba(255,255,255,0.5) !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.1) !important;
        outline: none !important;
    }
    
    .auth-container .stTabs [data-baseweb="tab-list"] button {
        color: rgba(255,255,255,0.5) !important;
        background: transparent !important;
    }
    
    .auth-container .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: white !important;
        border-bottom: 2px solid white !important;
    }
    
    .auth-container .stButton button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    
    .auth-container .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .auth-container .stAlert {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    .auth-container .stAlert div {
        color: white !important;
    }
    
    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .user-info {
        background: rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    section[data-testid="stSidebar"] .user-info div {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .avatar {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: rgba(255,255,255,0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stMetric label {
        color: rgba(255,255,255,0.7) !important;
    }
    section[data-testid="stSidebar"] .stMetric div {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] label {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
    }
    section[data-testid="stSidebar"] .stNumberInput label {
        color: white !important;
    }
    section[data-testid="stSidebar"] .stTextInput label {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stInfo {
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] .stInfo div {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stNumberInput input {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }
    
    section[data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }
    
    /* ========== MAIN AREA ========== */
    .quiz-card {
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        margin: 1rem 0 !important;
    }
    .quiz-card h3, .quiz-card div {
        color: white !important;
    }
    
    .option-btn {
        color: white !important;
        background: rgba(255,255,255,0.1) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        width: 100% !important;
        text-align: left !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
    }
    .option-btn:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: rgba(255,255,255,0.6) !important;
    }
    
    .result-card {
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        padding: 30px !important;
        text-align: center !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    .result-card h2, .result-card div {
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        color: rgba(255,255,255,0.7) !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: white !important;
        border-bottom: 2px solid white !important;
    }
    
    .main .stButton button {
        color: white !important;
        background: rgba(255,255,255,0.15) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
    }
    
    .main .stButton button:hover {
        background: rgba(255,255,255,0.25) !important;
    }
    
    .main .stButton button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        color: white !important;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    .stMetric label {
        color: rgba(255,255,255,0.8) !important;
    }
    .stMetric div {
        color: white !important;
    }
    
    .streamlit-expanderHeader {
        color: white !important;
    }
    
    .feedback-box {
        color: white !important;
        padding: 15px !important;
        border-radius: 8px !important;
        margin: 10px 0 !important;
        border-left: 4px solid !important;
    }
    .feedback-box.correct {
        background: rgba(40, 167, 69, 0.2) !important;
        border-color: #28a745 !important;
    }
    .feedback-box.wrong {
        background: rgba(220, 53, 69, 0.2) !important;
        border-color: #dc3545 !important;
    }
    .feedback-box div {
        color: white !important;
    }
    
    .history-item {
        color: white !important;
        padding: 10px !important;
        background: rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        border-left: 4px solid #667eea !important;
        margin: 5px 0 !important;
    }
    .history-item div {
        color: white !important;
    }
    
    .wrong-item {
        color: white !important;
        padding: 10px !important;
        background: rgba(220, 53, 69, 0.15) !important;
        border-radius: 8px !important;
        border-left: 4px solid #dc3545 !important;
        margin: 5px 0 !important;
    }
    .wrong-item div {
        color: white !important;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin: 20px 0;
    }
    .stat-card {
        background: rgba(255,255,255,0.1) !important;
        padding: 15px !important;
        border-radius: 10px !important;
        text-align: center !important;
        color: white !important;
        backdrop-filter: blur(10px) !important;
    }
    .stat-card h3, .stat-card div {
        color: white !important;
    }
    .score-display {
        font-size: 48px !important;
        font-weight: bold !important;
        color: white !important;
    }
    
    .debug-box {
        background: #1e1e1e !important;
        color: #00ff00 !important;
        padding: 15px !important;
        border-radius: 5px !important;
        font-family: monospace !important;
        font-size: 12px !important;
        white-space: pre-wrap !important;
        max-height: 300px !important;
        overflow: auto !important;
        margin: 10px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)


# ============ LOGIN PAGE ============

def login_page():
    st.markdown("""
        <div class="main-header">
            <h1>🧠 AI Quiz Master</h1>
            <p style="font-size: 18px; opacity: 0.9;">Login to start learning with AI-generated quizzes</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown("<h3>Welcome Back!</h3>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            if st.button("Login", key="login_btn", use_container_width=True):
                if auth_manager.login_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        with tab2:
            st.markdown("<h3>Create Account</h3>", unsafe_allow_html=True)
            new_username = st.text_input("Username", key="signup_username", placeholder="Choose a username")
            new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Password (min 6 chars)")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Confirm password")
            
            if st.button("Create Account", key="signup_btn", use_container_width=True):
                if not new_username or not new_password:
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif auth_manager.register_user(new_username, new_password):
                    st.success("✅ Account created! Please login.")
                else:
                    st.error("❌ Username already exists")
        
        st.markdown('</div>', unsafe_allow_html=True)


# ============ QUIZ MASTER CLASS ============

class QuizMaster:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_connected = False
        self.selected_model = ""
        self.debug_info = []
        self._test_connection()
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.topic = ""
        self.difficulty = "medium"
        self.total_questions = 0
        self.quiz_started = False
        self.quiz_completed = False
        self.user_answers = []
        self.start_time = None
        
    def _test_connection(self):
        self.debug_info = []
        if self.api_key:
            try:
                url = "https://api.groq.com/openai/v1/models"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    self.api_connected = True
                    st.session_state.api_status = "✅ API Connected!"
                    st.session_state.api_status_type = "success"
                    data = response.json()
                    available = [m["id"] for m in data.get("data", [])]
                    if available:
                        filtered = [
                            m for m in available 
                            if "guard" not in m.lower() 
                            and "prompt" not in m.lower()
                            and "arabic" not in m.lower()
                            and "orpheus" not in m.lower()
                            and "whisper" not in m.lower()
                            and "tts" not in m.lower()
                            and "embed" not in m.lower()
                        ]
                        preferred = [m for m in filtered if "llama" in m.lower() and "instruct" in m.lower()]
                        if preferred:
                            self.selected_model = preferred[0]
                        elif filtered:
                            self.selected_model = filtered[0]
                        self.debug_info.append(f"✅ Selected model: {self.selected_model}")
                else:
                    self.api_connected = False
                    st.session_state.api_status = f"⚠️ API Error: {response.status_code}"
                    st.session_state.api_status_type = "error"
                    self.debug_info.append(f"❌ API Error: {response.status_code}")
            except Exception as e:
                self.api_connected = False
                st.session_state.api_status = "⚠️ Connection Error"
                st.session_state.api_status_type = "error"
                self.debug_info.append(f"❌ Exception: {str(e)}")
        else:
            st.session_state.api_status = "⚠️ No API_KEY found in .env"
            st.session_state.api_status_type = "warning"
            self.debug_info.append("❌ No API_KEY found in .env")
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text, removing any thinking/explanation text"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find where the JSON actually starts (looking for [ or {)
        lines = text.split('\n')
        json_start = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('[') or stripped.startswith('{'):
                json_start = i
                break
        
        if json_start != -1:
            # Join only from the start of JSON
            text = '\n'.join(lines[json_start:])
        
        # Try to find JSON array pattern
        json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # Try to find JSON object pattern
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text
    
    def get_detailed_explanation(self, question: str, correct_answer: str, topic: str) -> str:
        if not self.api_key or not self.api_connected:
            return "💡 Please check API connection for detailed explanations."
        
        prompt = f"""Provide a detailed, easy-to-understand explanation for this question:
        
        Topic: {topic}
        Question: {question}
        Correct Answer: {correct_answer}
        
        Please provide:
        1. Why this is the correct answer
        2. A simple example to understand the concept
        3. Common misconceptions about this topic
        4. Tips to remember this concept
        
        Keep it concise but informative (max 150 words).
        """
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.selected_model,
                "messages": [
                    {"role": "system", "content": "You are a patient tutor providing clear explanations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return "💡 Could not fetch detailed explanation. Please try again."
        except Exception:
            return "💡 Could not fetch detailed explanation. Please try again."
    
    def generate_questions(self, topic: str, num_questions: int = 5, difficulty: str = "medium"):
        self.debug_info = []
        self.topic = topic
        self.difficulty = difficulty
        self.total_questions = num_questions
        self.quiz_started = True
        self.quiz_completed = False
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.start_time = datetime.now()
        
        st.session_state.show_feedback = False
        st.session_state.feedback = None
        
        self.debug_info.append(f"🚀 Generating quiz about: {topic}")
        self.debug_info.append(f"🔑 API Key present: {bool(self.api_key)}")
        self.debug_info.append(f"🔗 API Connected: {self.api_connected}")
        self.debug_info.append(f"🤖 Model: {self.selected_model}")
        
        if not self.api_key or not self.api_connected or not self.selected_model:
            self.debug_info.append("❌ Using fallback questions")
            self.questions = self._get_fallback_questions(topic, num_questions)
            return True
        
        if "whisper" in self.selected_model.lower() or "tts" in self.selected_model.lower():
            self.debug_info.append(f"❌ Model {self.selected_model} is not a chat model!")
            try:
                url = "https://api.groq.com/openai/v1/models"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    available = [m["id"] for m in data.get("data", [])]
                    filtered = [
                        m for m in available 
                        if "llama" in m.lower() 
                        and "instruct" in m.lower()
                        and "whisper" not in m.lower()
                        and "tts" not in m.lower()
                    ]
                    if filtered:
                        self.selected_model = filtered[0]
                        self.debug_info.append(f"🔄 Switched to: {self.selected_model}")
                    else:
                        self.debug_info.append("❌ No suitable chat model found!")
                        self.questions = self._get_fallback_questions(topic, num_questions)
                        return True
            except:
                self.questions = self._get_fallback_questions(topic, num_questions)
                return True
        
        prompt = f"""Generate {num_questions} multiple-choice questions about "{topic}".
Difficulty: {difficulty}.

CRITICAL INSTRUCTIONS:
1. Return ONLY a valid JSON array.
2. NO thinking process, NO explanations, NO markdown, NO additional text.
3. Start directly with [ and end with ].
4. All questions, options, and explanations MUST be in ENGLISH.

Format:
[
    {{
        "question": "Question text?",
        "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
        "correct_answer": "A",
        "explanation": "Brief explanation"
    }}
]"""
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.selected_model,
                "messages": [
                    {"role": "system", "content": "You are a quiz generator. Return ONLY valid JSON. Do not include any thinking process, explanations, or additional text. Only output the JSON array. No markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            }
            
            self.debug_info.append(f"📤 Sending request to Groq API...")
            
            with st.spinner(f"🧠 Generating {num_questions} questions about {topic}..."):
                response = requests.post(url, headers=headers, json=data, timeout=60)
                
                self.debug_info.append(f"📥 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    self.debug_info.append(f"📝 Response length: {len(content)} chars")
                    self.debug_info.append(f"📝 Preview: {content[:150]}...")
                    
                    clean_content = self._extract_json_from_text(content)
                    clean_content = clean_content.strip()
                    
                    self.debug_info.append(f"🧹 Cleaned: {clean_content[:150]}...")
                    
                    try:
                        self.questions = json.loads(clean_content)
                        self.debug_info.append(f"✅ Parsed {len(self.questions)} questions successfully!")
                        auth_manager.save_quiz(
                            st.session_state.username,
                            topic,
                            difficulty,
                            self.questions
                        )
                        return True
                    except json.JSONDecodeError as e:
                        self.debug_info.append(f"❌ JSON Parse Error: {e}")
                        try:
                            match = re.search(r'\[\s*\{.*\}\s*\]', clean_content, re.DOTALL)
                            if match:
                                self.questions = json.loads(match.group(0))
                                self.debug_info.append(f"✅ Extracted {len(self.questions)} questions using regex!")
                                return True
                        except:
                            pass
                        
                        self.debug_info.append("❌ Failed to parse JSON. Using fallback.")
                        self.questions = self._get_fallback_questions(topic, num_questions)
                        return True
                else:
                    self.debug_info.append(f"❌ API Error: {response.status_code}")
                    self.debug_info.append(f"Response: {response.text[:200]}")
                    self.questions = self._get_fallback_questions(topic, num_questions)
                    return True
        except Exception as e:
            self.debug_info.append(f"❌ Exception: {str(e)}")
            self.questions = self._get_fallback_questions(topic, num_questions)
            return True
    
    def _get_fallback_questions(self, topic: str, count: int) -> List[Dict]:
        return [
            {
                "question": f"Q{i+1}: What is a key concept in {topic}?",
                "options": ["A. Basic understanding", "B. Advanced knowledge", "C. Practical application", "D. Theoretical framework"],
                "correct_answer": "A",
                "explanation": f"💡 This is a fallback question."
            }
            for i in range(count)
        ]
    
    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
    
    def submit_answer(self, answer: str):
        question = self.get_current_question()
        if not question:
            return None
        
        is_correct = answer == question["correct_answer"]
        if is_correct:
            self.score += 1
        else:
            auth_manager.save_wrong_question(st.session_state.username, {
                "topic": self.topic,
                "question": question["question"],
                "correct_answer": question["correct_answer"],
                "user_answer": answer,
                "explanation": question["explanation"]
            })
            auth_manager.save_flashcard(st.session_state.username, {
                "topic": self.topic,
                "question": question["question"],
                "correct_answer": question["correct_answer"],
                "explanation": question["explanation"]
            })
        
        self.user_answers.append({
            "question": question["question"],
            "user_answer": answer,
            "correct_answer": question["correct_answer"],
            "is_correct": is_correct,
            "explanation": question["explanation"]
        })
        
        self.current_index += 1
        
        if self.current_index >= len(self.questions):
            self.quiz_completed = True
            self._save_quiz_history()
        
        return {
            "is_correct": is_correct,
            "explanation": question["explanation"],
            "correct_answer": question["correct_answer"]
        }
    
    def _save_quiz_history(self):
        duration = int((datetime.now() - self.start_time).seconds)
        percentage = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
        avg_time = duration / self.total_questions if self.total_questions > 0 else 0
        
        auth_manager.save_quiz_history(st.session_state.username, {
            "topic": self.topic,
            "difficulty": self.difficulty,
            "score": self.score,
            "total": self.total_questions,
            "percentage": percentage,
            "duration": duration,
            "avg_time": avg_time
        })
        
        auth_manager.save_study_session(st.session_state.username, {
            "total_questions": self.total_questions,
            "correct_answers": self.score,
            "time_spent": duration,
            "topics": self.topic
        })
    
    def get_score_percentage(self):
        if self.total_questions == 0:
            return 0
        return (self.score / self.total_questions) * 100
    
    def reset(self):
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.quiz_started = False
        self.quiz_completed = False
        self.start_time = None
        self.debug_info = []
        st.session_state.show_feedback = False
        st.session_state.feedback = None


# ============ UI FUNCTIONS ============

def show_history():
    st.markdown("### 📜 Quiz History")
    history = auth_manager.get_quiz_history(st.session_state.username)
    if not history:
        st.info("No quiz attempts yet. Take a quiz to see history here!")
        return
    
    df = pd.DataFrame(history)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Quizzes", len(df))
    with col2:
        st.metric("Average Score", f"{df['percentage'].mean():.1f}%")
    with col3:
        topics = df['topic'].value_counts()
        st.metric("Topics Studied", len(topics))
    with col4:
        avg_time = df['avg_time'].mean() if 'avg_time' in df.columns else 0
        st.metric("Avg Time/Q", f"{avg_time:.1f}s")
    
    st.markdown("---")
    for idx, row in df.head(10).iterrows():
        emoji = "🌟" if row['percentage'] >= 80 else "👍" if row['percentage'] >= 60 else "📖"
        duration_min = row['duration'] // 60
        duration_sec = row['duration'] % 60
        avg_time = row.get('avg_time', 0)
        st.markdown(f"""
            <div class="history-item">
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>{row['topic']}</strong> ({row['difficulty']})</span>
                    <span>{emoji} {row['percentage']:.0f}%</span>
                </div>
                <div style="color: #666; font-size: 12px;">
                    Score: {row['score']}/{row['total']} • 
                    Duration: {duration_min}:{duration_sec:02d} • 
                    Avg: {avg_time:.1f}s/q • 
                    {row['date']}
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_wrong_questions():
    st.markdown("### 🔄 Questions to Review")
    wrong_questions = auth_manager.get_wrong_questions(st.session_state.username)
    if not wrong_questions:
        st.info("🎉 No questions to review! You're doing great!")
        return
    
    st.write(f"Total questions to review: {len(wrong_questions)}")
    for q in wrong_questions:
        with st.expander(f"📌 {q['question'][:50]}..."):
            st.markdown(f"""
                <div class="wrong-item">
                    <div><strong>{q['question']}</strong></div>
                    <div>Your answer: <span style="color: #dc3545;">❌ {q['user_answer']}</span></div>
                    <div>Correct: <span style="color: #28a745;">✅ {q['correct_answer']}</span></div>
                    <div style="color: #666; font-size: 12px;">💡 {q['explanation']}</div>
                    <div style="color: #999; font-size: 10px;">
                        Topic: {q['topic']} • {q['date']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Mark All as Reviewed"):
            auth_manager.clear_wrong_questions(st.session_state.username)
            st.rerun()
    with col2:
        if st.button("🗑️ Clear All"):
            auth_manager.clear_wrong_questions(st.session_state.username)
            st.rerun()

def show_saved_quizzes():
    st.markdown("### 💾 Saved Quizzes")
    saved_quizzes = auth_manager.get_saved_quizzes(st.session_state.username)
    if not saved_quizzes:
        st.info("No saved quizzes yet. Generated quizzes are automatically saved!")
        return
    
    for quiz in saved_quizzes:
        with st.expander(f"📚 {quiz['topic']} ({quiz['difficulty']}) - {quiz['date']}"):
            st.write(f"Questions: {len(quiz['questions'])}")
            for i, q in enumerate(quiz['questions'], 1):
                st.write(f"{i}. {q['question']}")
                for opt in q['options']:
                    st.write(f"   {opt}")
                st.write(f"   ✅ Correct: {q['correct_answer']}")

def show_flashcards():
    st.markdown("### 🃏 Flashcards")
    flashcards = auth_manager.get_flashcards(st.session_state.username)
    if not flashcards:
        st.info("No flashcards yet. Wrong answers are automatically converted to flashcards!")
        return
    
    for card in flashcards:
        with st.expander(f"📌 {card['topic']} - Difficulty: {'⭐' * min(card['difficulty'], 5)}"):
            st.markdown(f"**Question:** {card['question']}")
            st.markdown(f"**Answer:** {card['correct_answer']}")
            st.markdown(f"**Explanation:** {card['explanation']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"⬆️ Easier", key=f"easy_{card['id']}"):
                    new_diff = max(1, card['difficulty'] - 1)
                    auth_manager.update_flashcard_difficulty(card['id'], new_diff)
                    st.rerun()
            with col2:
                if st.button(f"⬇️ Harder", key=f"hard_{card['id']}"):
                    new_diff = min(5, card['difficulty'] + 1)
                    auth_manager.update_flashcard_difficulty(card['id'], new_diff)
                    st.rerun()

def show_analytics():
    st.markdown("### 📊 Study Analytics")
    analytics = auth_manager.get_study_analytics(st.session_state.username)
    if not analytics["daily"]:
        st.info("Not enough data yet. Take more quizzes to see analytics!")
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    total_questions = sum(d["total"] for d in analytics["daily"])
    total_correct = sum(d["correct"] for d in analytics["daily"])
    total_time = sum(d["time"] for d in analytics["daily"])
    accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
    avg_time_per_q = total_time / total_questions if total_questions > 0 else 0
    
    with col1:
        st.metric("Total Questions", total_questions)
    with col2:
        st.metric("Correct Answers", total_correct)
    with col3:
        st.metric("Accuracy", f"{accuracy:.1f}%")
    with col4:
        st.metric("Time Spent", f"{total_time // 60}m")
    with col5:
        st.metric("Avg Time/Q", f"{avg_time_per_q:.1f}s")
    
    st.markdown("---")
    if analytics["topics"]:
        st.markdown("#### 📚 Topic Performance")
        df_topics = pd.DataFrame(analytics["topics"])
        st.dataframe(
            df_topics,
            column_config={
                "topic": "Topic",
                "total": "Questions",
                "pending": "Pending Review",
                "avg_time": st.column_config.NumberColumn("Avg Time (s)", format="%.1f"),
            },
            use_container_width=True
        )
    
    st.markdown("#### 📅 Recent Activity")
    df_daily = pd.DataFrame(analytics["daily"])
    if not df_daily.empty:
        st.line_chart(
            df_daily.set_index("date")[["total", "correct"]],
            use_container_width=True
        )

def export_results():
    history = auth_manager.get_quiz_history(st.session_state.username)
    if not history:
        st.info("No data to export")
        return
    
    df = pd.DataFrame(history)
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Quiz History (CSV)",
        data=csv,
        file_name=f"quiz_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# ============ MAIN APP ============

def main_app():
    # Sidebar with all features
    with st.sidebar:
        # User Profile
        st.markdown(f"""
            <div class="user-info">
                <div class="avatar">{st.session_state.username[0].upper()}</div>
                <div>
                    <div><strong>{st.session_state.username}</strong></div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 12px;">Logged in</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # API Status
        status_class = st.session_state.api_status_type
        st.markdown(f"""
            <div class="api-status {status_class}">
                {st.session_state.api_status}
            </div>
        """, unsafe_allow_html=True)
        
        # User Stats
        stats = auth_manager.get_user_stats(st.session_state.username)
        if stats:
            st.markdown("### 📊 Your Stats")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Quizzes", stats.get("quizzes_taken", 0))
            with col2:
                avg = (stats.get("total_score", 0) / stats.get("total_questions", 1)) * 100 if stats.get("total_questions", 0) > 0 else 0
                st.metric("Avg Score", f"{avg:.1f}%")
            with col3:
                total_time = stats.get("total_time", 0)
                st.metric("Total Time", f"{total_time // 60}m")
        
        st.markdown("---")
        
        # Logout Button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        
        st.markdown("---")
        
        # Quiz Settings
        st.markdown("### ⚙️ Quiz Settings")
        
        if 'quiz_master' not in st.session_state:
            st.session_state.quiz_master = QuizMaster()
        
        quiz = st.session_state.quiz_master
        
        if not quiz.quiz_started or quiz.quiz_completed:
            topic = st.text_input("📖 Topic", placeholder="e.g., Python, Machine Learning, History")
            num_questions = st.number_input("📝 Questions", min_value=1, max_value=20, value=5)
            difficulty = st.selectbox("📊 Difficulty", ["Easy", "Medium", "Hard"], index=1)
            
            if st.button("🚀 Generate Quiz", use_container_width=True, type="primary"):
                if topic:
                    quiz.generate_questions(topic, num_questions, difficulty.lower())
                    st.rerun()
                else:
                    st.warning("Please enter a topic")
        else:
            progress = quiz.current_index / quiz.total_questions if quiz.total_questions > 0 else 0
            st.progress(progress)
            st.markdown(f"**Question {quiz.current_index + 1}/{quiz.total_questions}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Score", f"{quiz.score}/{quiz.total_questions}")
            with col2:
                st.metric("Accuracy", f"{quiz.get_score_percentage():.0f}%")
            
            if st.button("🔄 Restart Quiz", use_container_width=True):
                quiz.reset()
                st.rerun()
        
        st.markdown("---")
        
        # Tips
        st.markdown("### 💡 Tips")
        st.info("• Read each question carefully\n• Take your time\n• Learn from explanations")
        st.info("💾 All data is saved permanently in database!")

    # Main Content Area
    st.markdown("""
        <div class="main-header">
            <h1>🧠 AI Quiz Master</h1>
            <p style="font-size: 18px; opacity: 0.9;">Test your knowledge with AI-generated quizzes</p>
        </div>
    """, unsafe_allow_html=True)
    
    if 'quiz_master' not in st.session_state:
        st.session_state.quiz_master = QuizMaster()
    
    quiz = st.session_state.quiz_master
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Quiz", 
        "📊 History", 
        "📚 Review", 
        "💾 Saved", 
        "🃏 Flashcards", 
        "📈 Analytics"
    ])
    
    with tab1:
        if not quiz.quiz_started:
            st.markdown("""
                <div style="text-align: center; padding: 40px 20px;">
                    <h2 style="font-size: 48px;">🧠</h2>
                    <h3>Ready to learn?</h3>
                    <p style="color: #666; font-size: 16px;">
                        Generate custom quizzes on any topic using AI.
                    </p>
                    <p style="color: #999; font-size: 14px;">
                        💾 All data saved permanently
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🔥 Popular Topics")
            topics = ["Python", "Machine Learning", "Web Development", "History", "Science"]
            cols = st.columns(5)
            for i, topic in enumerate(topics):
                with cols[i]:
                    if st.button(f"📚 {topic}", use_container_width=True):
                        quiz.generate_questions(topic, 5, "medium")
                        st.rerun()
        
        elif quiz.quiz_completed:
            percentage = quiz.get_score_percentage()
            
            auth_manager.update_stats(
                st.session_state.username, 
                quiz.score, 
                quiz.total_questions
            )
            
            emoji = "🌟" if percentage >= 90 else "👍" if percentage >= 70 else "📖" if percentage >= 50 else "💪"
            grade = "Outstanding!" if percentage >= 90 else "Good Job!" if percentage >= 70 else "Keep Learning!" if percentage >= 50 else "Keep Studying!"
            
            st.markdown(f"""
                <div class="result-card">
                    <h2>🎉 Quiz Complete!</h2>
                    <div style="font-size: 72px; margin: 20px 0;">{emoji}</div>
                    <div class="score-display">{quiz.score}/{quiz.total_questions}</div>
                    <div style="font-size: 24px; color: #666; margin: 10px 0;">
                        {percentage:.1f}%
                    </div>
                    <div style="font-size: 20px; margin: 20px 0;">{grade}</div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>✅ Correct</h3>
                            <div style="font-size: 32px; color: #28a745;">{quiz.score}</div>
                        </div>
                        <div class="stat-card">
                            <h3>❌ Incorrect</h3>
                            <div style="font-size: 32px; color: #dc3545;">{quiz.total_questions - quiz.score}</div>
                        </div>
                        <div class="stat-card">
                            <h3>📊 Accuracy</h3>
                            <div style="font-size: 32px; color: #667eea;">{percentage:.0f}%</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", use_container_width=True, type="primary"):
                    quiz.reset()
                    st.rerun()
            with col2:
                if st.button("📚 New Topic", use_container_width=True):
                    quiz.reset()
                    st.rerun()
            
            # ============ FIXED REVIEW SECTION ============
            with st.expander("📝 Review All Questions", expanded=False):
                for idx, answer in enumerate(quiz.user_answers, 1):
                    icon = "✅" if answer["is_correct"] else "❌"
                    color = "#28a745" if answer["is_correct"] else "#dc3545"
                    question_text = answer.get('question', '')
                    user_ans = answer.get('user_answer', '')
                    correct_ans = answer.get('correct_answer', '')
                    explanation = answer.get('explanation', '')
                    
                    st.markdown(f"""
                        <div style="padding: 15px; margin: 10px 0; border-left: 4px solid {color}; background: rgba(255,255,255,0.1); border-radius: 8px; backdrop-filter: blur(5px);">
                            <div><strong>{idx}. {question_text}</strong></div>
                            <div style="margin-top: 5px;">
                                <span>Your answer: </span>
                                <span style="color: {color}; font-weight: bold;">{user_ans}</span>
                            </div>
                            <div>
                                <span>Correct answer: </span>
                                <span style="color: #28a745; font-weight: bold;">{correct_ans}</span>
                            </div>
                            <div style="color: rgba(255,255,255,0.8); margin-top: 8px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                                💡 {explanation}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            with st.expander("💡 Get Detailed Explanation", expanded=False):
                if st.button("📖 Get AI Explanation"):
                    for answer in quiz.user_answers:
                        if not answer["is_correct"]:
                            st.markdown(f"**Question:** {answer['question']}")
                            st.markdown(f"**Correct Answer:** {answer['correct_answer']}")
                            explanation = quiz.get_detailed_explanation(
                                answer['question'],
                                answer['correct_answer'],
                                quiz.topic
                            )
                            st.markdown(f"**Explanation:** {explanation}")
                            st.markdown("---")
        
        else:
            current_q = quiz.get_current_question()
            if current_q:
                progress = quiz.current_index / quiz.total_questions
                st.markdown(f"""
                    <div class="progress-bar"><div class="progress-fill" style="width: {progress * 100}%;"></div></div>
                    <div class="quiz-card">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                            <span style="background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px;">
                                Question {quiz.current_index + 1}/{quiz.total_questions}
                            </span>
                            <span style="color: #666;">Topic: {quiz.topic}</span>
                        </div>
                        <h3>{current_q['question']}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                if not st.session_state.show_feedback:
                    cols = st.columns(2)
                    for idx, option in enumerate(current_q['options']):
                        with cols[idx % 2]:
                            if option.startswith(('A.', 'B.', 'C.', 'D.')):
                                letter = option[0]
                                text = option[2:].strip()
                            else:
                                letter = chr(65 + idx)
                                text = option
                            
                            if st.button(f"{letter}. {text}", use_container_width=True, key=f"opt_{idx}"):
                                result = quiz.submit_answer(letter)
                                if result:
                                    st.session_state.feedback = result
                                    st.session_state.show_feedback = True
                                    st.rerun()
                
                if st.session_state.show_feedback and st.session_state.feedback:
                    feedback = st.session_state.feedback
                    is_correct = feedback['is_correct']
                    
                    st.markdown(f"""
                        <div class="feedback-box {'correct' if is_correct else 'wrong'}">
                            <div style="font-size: 24px; font-weight: bold;">
                                {'✅ Correct!' if is_correct else '❌ Incorrect'}
                            </div>
                            <div><strong>Correct Answer:</strong> {feedback['correct_answer']}</div>
                            <div style="color: #555;">💡 <strong>Explanation:</strong> {feedback['explanation']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Next Question →", use_container_width=True, type="primary"):
                        st.session_state.show_feedback = False
                        st.session_state.feedback = None
                        if quiz.current_index >= quiz.total_questions:
                            quiz.quiz_completed = True
                        st.rerun()
    
    with tab2:
        show_history()
        st.markdown("---")
        export_results()
    
    with tab3:
        show_wrong_questions()
    
    with tab4:
        show_saved_quizzes()
    
    with tab5:
        show_flashcards()
    
    with tab6:
        show_analytics()
    
    if hasattr(quiz, 'debug_info') and quiz.debug_info:
        with st.expander("🔍 Debug Info", expanded=False):
            st.markdown('<div class="debug-box">' + "\n".join(quiz.debug_info) + '</div>', unsafe_allow_html=True)


# ============ APP ROUTING ============

if not st.session_state.authenticated:
    login_page()
else:
    main_app()
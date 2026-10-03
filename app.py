import streamlit as st
import wikipedia
import webbrowser
import random
import re
from datetime import datetime
from duckduckgo_search import DDGS

# --------------------------
# 🎨 PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="✨ AI Voice Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------
# 🎨 CUSTOM STYLING
# --------------------------
st.markdown("""
<style>
    * { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .main-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #2563eb, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .chat-box {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #2563eb;
    }
    .user-msg {
        background: #dbeafe;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
    }
    .assistant-msg {
        background: #f0f4f8;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        border-left: 3px solid #16a34a;
    }
    .fun-msg { border-left-color: #a855f7; }
    .info-msg { border-left-color: #2563eb; }
    .error-msg { border-left-color: #dc2626; }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .quick-btn button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# 💾 SESSION STATE — CHAT HISTORY
# --------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------
# 🧠 CORE LOGIC
# --------------------------
def get_internet_answer(query):
    if not query.strip():
        return "Please tell me what you want to know."
    
    # Step 1: Wikipedia
    try:
        wikipedia.set_lang("en")
        result = wikipedia.summary(query, sentences=3)
        return f"📚 From Wikipedia:\n{result}"
    except Exception:
        pass
    
    # Step 2: DuckDuckGo
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3, region="ph-en", safesearch="moderate"))
        if results:
            best = results[0]
            answer = f"{best['title']}\n{best['body']}"
            return answer if len(answer) < 500 else answer[:500] + "..."
        return "I found no clear answer for that."
    except Exception as e:
        return f"Search error: {str(e)}"

def tell_time_date():
    now = datetime.now()
    time_now = now.strftime("%I:%M %p")
    date_now = now.strftime("%A, %B %d, %Y")
    return f"🕒 Today is {date_now}, time is {time_now}"

def open_item(command):
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
        "facebook": "https://facebook.com",
        "wikipedia": "https://en.wikipedia.org",
        "maps": "https://maps.google.com",
    }
    for name, url in sites.items():
        if name in command:
            return f"Opening {name}...", url
    return "I don't know how to open that yet.", None

def fun_tools(command):
    if "joke" in command:
        jokes = [
            "Why robots never get lost? They always follow the right code!",
            "What do you call a sleeping robot? A power nap!",
            "Why do robots love music? They have great beats!",
            "Why was the computer cold? It left its Windows open!",
            "What’s a robot’s favorite snack? Microchips!"
        ]
        return "😄 " + random.choice(jokes), "fun"
    elif "motivate" in command or "inspire" in command:
        quotes = [
            "Believe you can and you're halfway there.",
            "Your only limit is your mind.",
            "Every day is a fresh start."
        ]
        return "💡 " + random.choice(quotes), "fun"
    elif "roll dice" in command:
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        return f"🎲 You rolled {d1} and {d2} — total {d1 + d2}", "fun"
    return None, None

def calculate(command):
    exp = re.sub(r"what is|calculate|plus|minus|times|divided by",
                 lambda m: {"plus": "+", "minus": "-", "times": "*", "divided by": "/"}.get(m.group(0), ""), command)
    exp = re.sub(r"one|two|three|four|five|six|seven|eight|nine|ten",
                 lambda m: {"one":"1", "two":"2", "three":"3", "four":"4", "five":"5",
                            "six":"6", "seven":"7", "eight":"8", "nine":"9", "ten":"10"}.get(m.group(0), ""), exp)
    try:
        result = eval(exp.strip(" ?"))
        return f"🧮 The answer is {result}", "info"
    except:
        return None, None

def process_command(command):
    command = command.lower().strip()
    
    if any(word in command for word in ["exit now", "goodbye", "close program", "shut down"]):
        return "🛑 Goodbye! Have a wonderful day!", "exit", None
    elif "time" in command or "date" in command or "day" in command:
        return tell_time_date(), "info", None
    elif "open" in command:
        msg, url = open_item(command)
        return msg, "info", url
    else:
        result, tag = fun_tools(command)
        if result: return result, tag, None
        result, tag = calculate(command)
        if result: return result, tag, None
        answer = get_internet_answer(command)
        return f"📌 Answer:\n{answer}", "info", None

# --------------------------
# � UI LAYOUT
# --------------------------
st.markdown("<h1 class='main-header'>✨ AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ask me anything — search, calculate, open sites, or just have fun!</p>", unsafe_allow_html=True)

# Quick Buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🕒 Time", use_container_width=True):
        st.session_state.input_text = "time"
with col2:
    if st.button("😄 Joke", use_container_width=True):
        st.session_state.input_text = "tell me a joke"
with col3:
    if st.button("💡 Motivate", use_container_width=True):
        st.session_state.input_text = "motivate me"
with col4:
    if st.button("🎲 Roll Dice", use_container_width=True):
        st.session_state.input_text = "roll dice"

# Input
user_input = st.text_input("💬 Type your question:", 
                          value=st.session_state.get("input_text", ""),
                          placeholder="Ask me anything...",
                          key="text_input")

if st.button("🚀 Send", type="primary", use_container_width=True) and user_input:
    # Add user message
    st.session_state.history.append(("user", user_input))
    
    # Process
    reply, tag, url = process_command(user_input)
    
    # Add assistant reply
    st.session_state.history.append(("assistant", reply, tag, url))
    
    # Clear input
    st.session_state.input_text = ""

# Display Chat History
st.markdown("---")
for msg in st.session_state.history:
    if msg[0] == "user":
        st.markdown(f"<div class='chat-box user-msg'><strong>You:</strong> {msg[1]}</div>", unsafe_allow_html=True)
    else:
        tag_class = f"{msg[2]}-msg" if len(msg) > 2 else ""
        st.markdown(f"<div class='chat-box assistant-msg {tag_class}'><strong>Assistant:</strong> {msg[1]}</div>", unsafe_allow_html=True)
        if len(msg) > 3 and msg[3]:
            st.markdown(f"🔗 [Open Link]({msg[3]}) — will open in new tab")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center; color:#94a3b8; padding:1rem;'>Made with Jayson Pepito | Your AI Assistant — Powered by Streamlit</div>", unsafe_allow_html=True)

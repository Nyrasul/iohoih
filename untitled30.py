import streamlit as st
import json
import random

# Page Config
st.set_page_config(page_title="MedQuiz Master", layout="centered")

# Load Data
@st.cache_data
def load_data():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)

questions = load_data()

# Initialize Session State
if 'shuffled_questions' not in st.session_state:
    st.session_state.shuffled_questions = questions.copy()
    random.shuffle(st.session_state.shuffled_questions)

if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'bookmarked' not in st.session_state: st.session_state.bookmarked = set()

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Settings")
if st.sidebar.button("🔄 Shuffle Questions"):
    random.shuffle(st.session_state.shuffled_questions)
    st.session_state.current_q = 0
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("### Bookmarked Questions")
for b in st.session_state.bookmarked:
    st.sidebar.write(f"Q: {b}")

# --- Quiz Logic ---
q_data = st.session_state.shuffled_questions[st.session_state.current_q]

st.title("⚕️ Medical Prep Quiz")
st.progress((st.session_state.current_q + 1) / len(st.session_state.shuffled_questions))

# Question Display
st.subheader(f"Q{st.session_state.current_q + 1}: {q_data['question']}")

# Display Images if they exist
if q_data.get("images"):
    for img in q_data["images"]:
        st.image(img, use_container_width=True)

# Answer Handling
key = f"q_{st.session_state.current_q}"
selected = st.radio("Select answer:", q_data["options"], key=key)

# Comfort Buttons
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("Previous"):
        if st.session_state.current_q > 0: st.session_state.current_q -= 1; st.rerun()
with c2:
    if st.button("🔖 Bookmark"):
        st.session_state.bookmarked.add(q_data['question'])
with c3:
    if st.button("Next"):
        if st.session_state.current_q < len(st.session_state.shuffled_questions) - 1:
            st.session_state.current_q += 1; st.rerun()

# Immediate Feedback (Comfort feature: toggleable)
if st.checkbox("Show Correct Answer Immediately"):
    if selected == q_data["correct_answer"]:
        st.success("Correct!")
    else:
        st.error(f"Try again! Correct was: {q_data['correct_answer']}")

import streamlit as st
import json
import random

# Load Data
@st.cache_data
def load_data():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)

questions = load_data()

st.sidebar.header("🎯 Test Configuration")

# 1. Filter Setup
sources = list(set([q.get('source', 'Unknown') for q in questions]))
selected_sources = st.sidebar.multiselect("Select Files to Include:", sources, default=sources)
filtered_questions = [q for q in questions if q.get('source', 'Unknown') in selected_sources]

# 2. Slider Setup (Safe)
max_q = len(filtered_questions)
if max_q > 0:
    num_q = st.sidebar.slider("Number of Questions:", 1, max_q, min(20, max_q))

    # --- START NEW TEST ---
    if st.sidebar.button("🚀 Start New Test"):
        st.session_state.quiz_data = random.sample(filtered_questions, num_q)
        st.session_state.current_q = 0
        st.session_state.user_answers = {}
        st.session_state.failed_questions = [] # Reset failures
        st.rerun()
else:
    st.sidebar.warning("No questions match your selection.")

# --- MAIN APP ---
if 'quiz_data' not in st.session_state:
    st.title("⚕️ Medical Prep Quiz")
    st.info("Configure your test in the sidebar and click 'Start New Test'.")
else:
    q_data = st.session_state.quiz_data[st.session_state.current_q]
    
    st.subheader(f"Question {st.session_state.current_q + 1} / {len(st.session_state.quiz_data)}")
    st.write(q_data['question'])
    
    if q_data.get("images"):
        for img in q_data["images"]: st.image(img, use_container_width=True)

    # Radio selection
    ans = st.radio("Choose:", q_data['options'], key=f"q_{st.session_state.current_q}")
    st.session_state.user_answers[st.session_state.current_q] = ans

    # Navigation
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Previous") and st.session_state.current_q > 0:
        st.session_state.current_q -= 1; st.rerun()
    if c2.button("Next ➡️") and st.session_state.current_q < len(st.session_state.quiz_data) - 1:
        st.session_state.current_q += 1; st.rerun()

    # Submit
    if st.session_state.current_q == len(st.session_state.quiz_data) - 1:
        if st.button("Submit Test"):
            # Calculate Score & Track Failures
            st.session_state.failed_questions = []
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                if st.session_state.user_answers.get(i) == q['correct_answer']:
                    score += 1
                else:
                    st.session_state.failed_questions.append(q)
            
            st.metric("Final Score", f"{score} / {len(st.session_state.quiz_data)}")
            
            # --- RETEST FAILED OPTION ---
            if st.session_state.failed_questions:
                if st.button("🔄 Retest Failed Questions"):
                    st.session_state.quiz_data = st.session_state.failed_questions
                    st.session_state.current_q = 0
                    st.session_state.user_answers = {}
                    st.rerun()

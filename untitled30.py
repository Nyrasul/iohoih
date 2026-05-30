import streamlit as st
import json
import random
 
# Load Data
@st.cache_data
def load_data():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)

questions = load_data()

# --- SIDEBAR: Filter Controls ---
st.sidebar.header("🎯 Test Configuration")

# Get unique file sources
sources = list(set([q.get('source', 'Unknown') for q in questions]))
selected_sources = st.sidebar.multiselect("Select Files to Include:", sources, default=sources)

# Filter questions by selected files - ADDED .get() HERE
filtered_questions = [q for q in questions if q.get('source', 'Unknown') in selected_sources] 

# Select Number of Questions
max_q = len(filtered_questions)
num_q = st.sidebar.slider("Number of Questions:", 5, max_q, min(20, max_q))

if st.sidebar.button("🚀 Start New Test"):
    st.session_state.quiz_data = random.sample(filtered_questions, num_q)
    st.session_state.current_q = 0
    st.session_state.user_answers = {}
    st.rerun()

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
            # Calculate Score
            score = sum(1 for i, q in enumerate(st.session_state.quiz_data) 
                        if st.session_state.user_answers.get(i) == q['correct_answer'])
            st.metric("Final Score", f"{score} / {len(st.session_state.quiz_data)}")

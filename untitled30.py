import streamlit as st
import json
import random

@st.cache_data
def load_data():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)

questions = load_data()

st.sidebar.header("🎯 Test Configuration")
sources = list(set([q.get('source', 'Unknown') for q in questions]))
selected_sources = st.sidebar.multiselect("Select Files to Include:", sources, default=sources)
filtered_questions = [q for q in questions if q.get('source', 'Unknown') in selected_sources]

max_q = len(filtered_questions)
if max_q > 0:
    num_q = st.sidebar.slider("Number of Questions:", 1, max_q, min(20, max_q))
    if st.sidebar.button("🚀 Start New Test"):
        st.session_state.quiz_data = random.sample(filtered_questions, num_q)
        st.session_state.current_q = 0
        st.session_state.user_answers = {}
        st.session_state.show_results = False
        st.session_state.failed_questions = []
        st.rerun()
else:
    st.sidebar.warning("No questions match your selection.")

# --- MAIN QUIZ UI ---
if 'quiz_data' not in st.session_state:
    st.title("⚕️ Medical Prep Quiz")
    st.info("Configure your test in the sidebar and click 'Start New Test'.")
else:
    q_data = st.session_state.quiz_data[st.session_state.current_q]
    
    st.subheader(f"Question {st.session_state.current_q + 1} / {len(st.session_state.quiz_data)}")
    st.write(q_data['question'])
    
    if q_data.get("images"):
        for img in q_data["images"]: st.image(img, use_container_width=True)

    # Radio Selection
    ans = st.radio("Choose:", q_data['options'], key=f"q_{st.session_state.current_q}")
    st.session_state.user_answers[st.session_state.current_q] = ans

    # --- FEEDBACK LOGIC ---
    if st.button("Check Answer"):
        st.session_state.show_results = True
        
    if st.session_state.get('show_results', False):
        if st.session_state.user_answers[st.session_state.current_q] == q_data['correct_answer']:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! Correct answer: {q_data['correct_answer']}")

    # Navigation
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Previous") and st.session_state.current_q > 0:
        st.session_state.current_q -= 1; st.session_state.show_results = False; st.rerun()
    if c2.button("Next ➡️") and st.session_state.current_q < len(st.session_state.quiz_data) - 1:
        st.session_state.current_q += 1; st.session_state.show_results = False; st.rerun()

    # Submit & Retest Logic
    if st.session_state.current_q == len(st.session_state.quiz_data) - 1:
        if st.button("Submit Test"):
            st.session_state.failed_questions = [
                q for i, q in enumerate(st.session_state.quiz_data) 
                if st.session_state.user_answers.get(i) != q['correct_answer']
            ]
            
            score = len(st.session_state.quiz_data) - len(st.session_state.failed_questions)
            st.metric("Final Score", f"{score} / {len(st.session_state.quiz_data)}")
            
            if st.session_state.failed_questions:
                st.warning(f"You missed {len(st.session_state.failed_questions)} questions.")
                if st.button("🔄 Retest Failed Questions"):
                    st.session_state.quiz_data = st.session_state.failed_questions
                    st.session_state.current_q = 0
                    st.session_state.user_answers = {}
                    st.session_state.show_results = False
                    st.rerun()

import streamlit as st
from sunbeam_llm import ask_question

st.set_page_config(
    page_title="Sunbeam Course Chatbot",
    page_icon="🎓",
    layout="wide"
)
#session state
if "chat_history" not in st.session_state:
    # chat_history = [(role, message)]
    st.session_state.chat_history = []

#sidebar
with st.sidebar:
    st.title("🧾 Your Questions")
    st.markdown("---")

    # get only user questions and reverse (latest first)
    user_questions = [
        msg for role, msg in st.session_state.chat_history if role == "user"
    ][::-1]

    if user_questions:
        for q in user_questions:
            st.markdown(f"- {q}")   
    else:
        st.caption("No questions asked yet")

    st.markdown("---")

    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


st.title("🎓 Sunbeam Course Chatbot")
st.caption("Ask anything about Sunbeam courses, fees, duration, eligibility")

#chat history
for role, message in st.session_state.chat_history:
    if role == "user":
        st.chat_message("user", avatar="👤").write(message)
    else:
        st.chat_message("assistant", avatar="🤖").write(message)

#chat inputs
user_query = st.chat_input("Ask about courses, fees, duration, eligibility...")

if user_query and user_query.strip():
    
    st.chat_message("user", avatar="👤").write(user_query)
    st.session_state.chat_history.append(("user", user_query))

    
    with st.spinner("Thinking..."):
        try:
            response = ask_question(user_query)
        except Exception as e:
            response = f"⚠️ Error: {e}"

    st.chat_message("assistant", avatar="🤖").write(response)
    st.session_state.chat_history.append(("assistant", response))

"""Run with: python -m streamlit run streamlit_app.py"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from coach import LEVELS, create_session, evaluate_answer

# Load a local .env file without overriding existing environment variables.
load_dotenv(Path(__file__).with_name(".env"))
st.set_page_config(page_title="AI Learning Coach", page_icon=":material/school:", layout="centered")

# Streamlit reruns this script after interactions. Session state retains your work.
for name, default in {
    "learning_session": None, "feedback": None, "evaluated_answer": "",
    "answer": "", "topic": "", "level": "Beginner",
    "lesson_activity": [], "feedback_activity": [],
}.items():
    st.session_state.setdefault(name, default)


def reset_learning():
    """Callbacks run before widgets render, so clearing their values here is safe."""
    st.session_state.update(
        learning_session=None, feedback=None, evaluated_answer="", answer="", topic="",
        lesson_activity=[], feedback_activity=[],
    )


def activity_reporter(state_key, display):
    """Update one persistent text display as synchronous crew tasks finish."""
    st.session_state[state_key] = []

    def report(message):
        st.session_state[state_key].append(message)
        display.code("\n".join(st.session_state[state_key]), language=None, wrap_lines=True)

    return report


def show_request_error(error):
    """Never show raw provider exceptions, which may contain request details."""
    if isinstance(error, ValueError):
        st.error(str(error))
    else:
        st.error(
            "The AI request could not finish. Check your API key, model access, API credits, "
            "and internet connection, then try again. Your current work is still here."
        )


st.title("AI Learning Coach")
st.markdown("Learn something new. Put it into practice. Get feedback that helps you grow.")

api_key = os.getenv("OPENAI_API_KEY", "").strip()
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

with st.sidebar:
    st.subheader("Connection")
    st.caption("API key configured" if api_key else "Set OPENAI_API_KEY in .env to start learning.")
    st.caption("Generating lessons and feedback uses your OpenAI API credits.")
    with st.expander("Meet your learning crew"):
        st.markdown("**1 · AI Tutor** explains the topic and gives examples.")
        st.markdown("**2 · Exercise Designer** builds practice from that lesson.")
        st.markdown("**3 · Learning Evaluator** reviews your answer and suggests improvements.")
    st.button("Start a new topic", on_click=reset_learning, icon=":material/refresh:", width="stretch")

with st.container(border=True):
    st.subheader("1 · Choose what to learn")
    # A form batches typing and selection changes. Only submission calls the API.
    with st.form("learning_form"):
        topic = st.text_input("What would you like to learn?", key="topic", max_chars=200,
                              placeholder="For example, Python functions")
        level = st.selectbox("Your experience level", LEVELS, key="level")
        generate = st.form_submit_button("Create my lesson", type="primary", width="stretch")
    lesson_activity_display = st.empty()
    if st.session_state.lesson_activity:
        lesson_activity_display.code("\n".join(st.session_state.lesson_activity), language=None, wrap_lines=True)
    if generate:
        if not topic.strip():
            st.warning("Enter a topic first, such as Python functions.")
        elif not api_key:
            st.warning("Set OPENAI_API_KEY in your .env file, then restart the app.")
        else:
            report = activity_reporter("lesson_activity", lesson_activity_display)
            try:
                with st.spinner("Your tutor and exercise designer are preparing your session…"):
                    new_session = create_session(topic, level, api_key, model, on_progress=report)
                # Commit only on success: a failed request never erases the previous lesson.
                st.session_state.update(
                    learning_session=new_session, feedback=None, evaluated_answer="", answer="",
                    feedback_activity=[],
                )
            except Exception as error:
                report("Lesson crew: Request stopped. Your previous work is preserved; check the message below.")
                show_request_error(error)

session = st.session_state.learning_session
if session is None:
    st.info("Choose a topic and a level to receive your first lesson and exercise.")
else:
    st.caption(f"Current session: {session.topic} · {session.level}")
    with st.container(border=True):
        st.subheader("2 · Your personalised lesson")
        st.caption("Prepared by your AI Tutor")
        st.markdown(session.lesson)

    with st.container(border=True):
        st.subheader("3 · Try it yourself")
        st.markdown(f"**{session.exercise.title}**")
        st.markdown(session.exercise.instructions)
        with st.expander("Need a hint?"):
            st.markdown(session.exercise.hint)
        with st.form("answer_form"):
            answer = st.text_area("Your answer", key="answer", height=200, max_chars=12000,
                                  placeholder="Write your explanation or paste your code here…")
            submit = st.form_submit_button("Get feedback", type="primary", width="stretch")
        feedback_activity_display = st.empty()
        if st.session_state.feedback_activity:
            feedback_activity_display.code("\n".join(st.session_state.feedback_activity), language=None, wrap_lines=True)
        if submit:
            if not answer.strip():
                st.warning("Write an answer before requesting feedback.")
            elif not api_key:
                st.warning("Set OPENAI_API_KEY in your .env file, then restart the app.")
            else:
                report = activity_reporter("feedback_activity", feedback_activity_display)
                try:
                    with st.spinner("Your learning evaluator is reviewing your answer…"):
                        feedback = evaluate_answer(session, answer, api_key, model, on_progress=report)
                    st.session_state.update(feedback=feedback, evaluated_answer=answer.strip())
                except Exception as error:
                    report("Learning Evaluator: Request stopped. Your previous work is preserved; check the message below.")
                    show_request_error(error)

    if st.session_state.feedback:
        with st.container(border=True):
            st.subheader("4 · Your feedback")
            st.markdown(st.session_state.feedback)
            # Preserve the exact answer reviewed, even if the learner starts editing a revision.
            with st.expander("Answer this feedback refers to"):
                st.text(st.session_state.evaluated_answer)
            st.caption("Revise your answer and select Get feedback again, or start a new topic.")

st.caption("AI responses can make mistakes. Sessions last for this browser connection. Submitted code is reviewed, not executed.")

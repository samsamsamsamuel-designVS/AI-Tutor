# Your first CrewAI AI Learning Coach

A small Python app with a simple Streamlit interface and three specialised CrewAI agents, following your reference diagram. Enter a topic and experience level, read a lesson, attempt an exercise, receive constructive feedback, and revise your answer or start another topic.

## Run it on Windows

Use Python 3.12. Open PowerShell in this project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Set `OPENAI_API_KEY` in `.env` to your API key and `OPENAI_MODEL` to your preferred model (default: `gpt-4o-mini`), save the file, then run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the local URL printed in the terminal, usually http://localhost:8501. Stop the app with Ctrl+C. The API key and model are loaded from `.env`; restart the app after changing them. Existing environment variables take precedence over `.env` values.

The current machine already has the dependencies installed, so you can also start with `python -m streamlit run streamlit_app.py`.

## Try your first session

1. Enter **Python functions** and choose **Beginner**.
2. Select **Create my lesson**. The tutor explains the topic and the designer creates an exercise based on that lesson.
3. Read the lesson, attempt the exercise, and optionally open the hint.
4. Type or paste your answer, then select **Get feedback**.
5. Revise your answer and request feedback again, or select **Start a new topic**.

A live text display appears above each result, showing the active agent, the tutor-to-designer handoff, and task completion. These activity summaries persist across interactions and clear when you start a new topic. They describe workflow milestones rather than private internal reasoning; the exercise's marking guide and reference solution stay private.

Each generation and evaluation uses your OpenAI API credits. Model availability depends on your account; change `OPENAI_MODEL` in `.env` if needed and restart the app. A failed request preserves your current lesson and answer so you can retry.

## Learn how the code works

- `streamlit_app.py`: the interface, API settings, input forms, and session state. Streamlit reruns the script when you interact; `st.session_state` retains the lesson, answer, and feedback. Forms prevent API calls while typing.
- `coach.py`: the three agents and their tasks. An **Agent** has a role, goal, and backstory. A **Task** describes an assignment and expected output. A **Crew** runs the agents' tasks.
- `create_session()`: the tutor and designer run in `Process.sequential` order. `context=[lesson_task]` passes the lesson to the exercise designer. Pydantic's `Exercise` model separates public instructions and hints from the private rubric and solution.
- `evaluate_answer()`: after the human submits an answer, a second crew runs the evaluator with the stored lesson, exercise, rubric, and answer. This human pause is why evaluation is separate from lesson generation. It does not regenerate the lesson.
- `.streamlit/config.toml`: a simple dark theme with a green accent inspired by your reference.

To experiment, edit each agent's `goal` or `backstory`, the lesson's requested headings, or the feedback sections. Comments explain the key decisions next to the code.

The agents use CrewAI's native OpenAI integration. Submitted topics and answers go to OpenAI; code is never executed. CrewAI tracing and telemetry are disabled by this app. AI feedback can be wrong, and sessions are temporary: closing the connection or restarting the server can clear them. Do not commit `.env` or share your API key.

## Verification

Run the offline tests without spending API credits:

```powershell
python -m unittest discover -s tests -v
```

Tests simulate the AI responses to check lesson handoff, evaluation context, input validation, form submission, retries, and reset behavior. A real API call requires your configured key and available credits.

Official references: [CrewAI tasks](https://docs.crewai.com/en/concepts/tasks), [CrewAI LLM configuration](https://docs.crewai.com/en/concepts/llms), and [Streamlit session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state).

import streamlit as st
import requests
import json
from model import QuestionBank, Evaluator, InterviewSession, ReportGenerator, DataManager

st.set_page_config(page_title="Interview Simulator", page_icon="🎯", layout="centered")

# ── Session state init ──────────────────────────────────────────
if "session"    not in st.session_state: st.session_state.session    = None
if "current_q"  not in st.session_state: st.session_state.current_q  = None
if "last_eval"  not in st.session_state: st.session_state.last_eval  = None

qb         = QuestionBank()
evaluator  = Evaluator()
report_gen = ReportGenerator()
data_mgr   = DataManager()

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎯 Interview Simulator")
    st.divider()

    page = st.radio("Navigate", ["🏠 Home", "🎤 Interview", "📊 Report", "📚 History"])
    st.divider()

    st.subheader("Session Setup")
    name       = st.text_input("Your Name", value="Candidate")
    q_type     = st.selectbox("Category", ["Mixed"] + list(qb.all_types))
    difficulty = st.selectbox("Difficulty", ["Any", "Easy", "Medium", "Hard"])
    use_ai     = st.toggle("AI Evaluation", value=True)
    api_key    = ""
    if use_ai:
        api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")

    st.divider()
    sess = st.session_state.session
    if sess and not sess.is_empty():
        st.metric("Questions Done", sess.question_count)
        st.metric("Avg Score", f"{sess.total_score} / 10")

    if st.button("🔄 Reset Session"):
        st.session_state.session   = None
        st.session_state.current_q = None
        st.session_state.last_eval = None
        st.rerun()

# ── AI evaluation ────────────────────────────────────────────────
def ai_evaluate(question, answer, key):
    prompt = f"""You are a strict and critical interviewer. Evaluate the answer VERY STRICTLY.

MOST IMPORTANT RULE:
- If the answer is completely unrelated to the question topic, give score 0 to 2. No exceptions.
- If the answer is about a different domain (e.g., HR answer to a Technical question), give score 0 to 2.
- If the answer contains no relevant technical/domain keywords for the question, give score 0 to 2.
- Only give a high score if the answer directly and correctly addresses the question.

Evaluation criteria (in order of importance):
1. Relevance — does the answer actually address this specific question?
2. Correctness — are the concepts accurate?
3. Depth & clarity — are details and examples provided?
4. Completeness — are all key points covered?

Question Type: {question.qtype} | Difficulty: {question.difficulty}
Question: {question.text}
Answer: {answer}

Identify if the answer is:
- Irrelevant (completely off-topic or wrong domain)
- Contradictory (says the opposite of what is correct)
- Incorrect (factually wrong)

Respond ONLY with valid JSON (no markdown):
{{
  "score": <float 0-10>,
  "grade": "<Excellent|Good|Average|Needs Improvement>",
  "is_irrelevant": <true|false>,
  "is_contradictory": <true|false>,
  "is_incorrect": <true|false>,
  "strengths": ["..."],
  "improvements": ["..."],
  "ideal_points": ["..."],
  "overall_feedback": "<2-3 sentences>"
}}"""
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 1000,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=25,
        )
        text = r.json()["content"][0]["text"].strip()
        if text.startswith("```"):
            text = text.split("```")[1].lstrip("json").strip()
        p = json.loads(text)
        return {
            "score":            float(p.get("score", 5)),
            "grade":            p.get("grade", "Average"),
            "is_irrelevant":    p.get("is_irrelevant", False),
            "is_contradictory": p.get("is_contradictory", False),
            "is_incorrect":     p.get("is_incorrect", False),
            "strengths":        p.get("strengths", []),
            "improvements":     p.get("improvements", []),
            "ideal_points":     p.get("ideal_points", []),
            "ai_feedback":      p.get("overall_feedback", ""),
            "tips":             p.get("improvements", []),
            "ai_powered":       True,
            "word_count":       len(answer.split()),
        }
    except Exception:
        return {}

def fetch_question():
    t = None if q_type == "Mixed" else q_type
    d = None if difficulty == "Any" else difficulty
    try:
        st.session_state.current_q = qb.get_random(qtype=t, difficulty=d)
    except ValueError:
        st.session_state.current_q = qb.get_random()

# ════════════════════════════════════════════════════════════════
# PAGE: Home
# ════════════════════════════════════════════════════════════════
if "Home" in page:
    st.title("🎯 Smart Interview Simulator")
    st.caption("Practice HR, Technical, DSA, Behavioural & System Design questions with AI feedback.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", len(qb))
    col2.metric("Categories", 5)
    col3.metric("Difficulty Levels", 3)

    st.divider()
    st.subheader("How It Works")
    st.markdown("""
1. Set your **name**, **category**, and **difficulty** in the sidebar
2. Go to **Interview** to start answering questions
3. Submit each answer to get a score + feedback
4. View your full **Report** when done
5. Past sessions are saved in **History**
""")

    st.subheader("OOP Architecture")
    st.markdown("""
| Class | Role |
|---|---|
| `Question` | Stores question text, type, difficulty, tags |
| `QuestionBank` | 30+ questions with filter support |
| `Evaluator` | Rule-based fallback scoring |
| `InterviewSession` | Tracks all responses & computes stats |
| `ReportGenerator` | Builds report dict + Markdown export |
| `DataManager` | Saves/loads session history as JSON |
""")

# ════════════════════════════════════════════════════════════════
# PAGE: Interview
# ════════════════════════════════════════════════════════════════
elif "Interview" in page:
    st.title("🎤 Interview")

    if st.session_state.session is None:
        st.session_state.session = InterviewSession(
            candidate_name=name,
            mode="Mixed" if q_type == "Mixed" else "Focused"
        )

    if st.session_state.current_q is None:
        fetch_question()

    q = st.session_state.current_q
    sess = st.session_state.session

    st.caption(f"Q{sess.question_count + 1} · {q.qtype} · {q.difficulty}")
    st.subheader(q.text)
    if q.tags:
        st.caption("Tags: " + ", ".join(f"#{t}" for t in q.tags))

    st.divider()
    answer = st.text_area("Your Answer", height=160,
                          placeholder="Be detailed — use examples and explain your reasoning.")
    st.caption(f"{len(answer.split()) if answer.strip() else 0} words")

    col1, col2, col3 = st.columns(3)
    submit = col1.button("✅ Submit", use_container_width=True)
    skip   = col2.button("⏭ Skip",   use_container_width=True)
    nxt    = col3.button("➡ Next",   use_container_width=True)

    if skip or nxt:
        fetch_question()
        st.session_state.last_eval = None
        st.rerun()

    if submit:
        if not answer.strip():
            st.warning("Write an answer before submitting.")
        else:
            with st.spinner("Evaluating…"):
                ev = (ai_evaluate(q, answer, api_key) if use_ai and api_key else {}) or evaluator.evaluate(answer, question=q)
            sess.record(q, answer, ev)
            st.session_state.last_eval = ev
            fetch_question()
            st.rerun()

    # ── Result ───────────────────────────────────────────────────
    ev = st.session_state.last_eval
    if ev:
        st.divider()
        st.subheader("📝 Evaluation")

        col1, col2, col3 = st.columns(3)
        col1.metric("Score",      f"{ev['score']} / 10")
        col2.metric("Grade",      ev['grade'])
        col3.metric("Word Count", ev.get('word_count', 0))

        st.progress(ev['score'] / 10)

        if ev.get("ai_powered"):
            # ── Answer quality flags ──────────────────────────────
            flags = []
            if ev.get("is_irrelevant"):    flags.append("⚠️ Irrelevant")
            if ev.get("is_contradictory"): flags.append("❌ Contradictory")
            if ev.get("is_incorrect"):     flags.append("❌ Incorrect")
            if flags:
                st.error("**Answer Issues Detected:** " + "  |  ".join(flags))

            st.info(f"🤖 **AI Feedback:** {ev['ai_feedback']}")
            if ev.get("strengths"):
                st.success("**✅ Strengths:**\n" + "\n".join(f"- {s}" for s in ev["strengths"]))
            if ev.get("improvements"):
                st.warning("**💡 Improve:**\n" + "\n".join(f"- {i}" for i in ev["improvements"]))
            if ev.get("ideal_points"):
                st.info("**📌 Key Points to Include:**\n" + "\n".join(f"- {p}" for p in ev["ideal_points"]))
        else:
            if ev.get("tips"):
                st.warning("**Tips:**\n" + "\n".join(f"- {t}" for t in ev["tips"]))

        st.caption("👉 A new question is ready above.")

# ════════════════════════════════════════════════════════════════
# PAGE: Report
# ════════════════════════════════════════════════════════════════
elif "Report" in page:
    st.title("📊 Report")

    sess = st.session_state.session
    if not sess or sess.is_empty():
        st.info("Complete at least one question first.")
    else:
        report = report_gen.generate(sess)

        col1, col2, col3 = st.columns(3)
        col1.metric("Questions", report["questions_attempted"])
        col2.metric("Avg Score", f"{report['average_score']} / 10")
        col3.metric("Grade",     report["overall_grade"])

        st.divider()
        st.subheader("Score by Category")
        for qtype, score in report["score_by_type"].items():
            st.write(f"**{qtype}** — {score}/10")
            st.progress(score / 10)

        if report["strengths"]:
            st.success("✅ Strong in: " + ", ".join(report["strengths"]))
        if report["weak_areas"]:
            st.warning("⚠️ Focus on: " + ", ".join(report["weak_areas"]))

        st.divider()
        st.subheader("Response Log")
        for entry in report["responses"]:
            with st.expander(f"Q{entry['index']} · {entry['type']} · {entry['score']}/10 — {entry['question'][:55]}…"):
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown(f"**Answer:** {entry['answer']}")
                st.markdown(f"**Grade:** {entry['grade']}  |  **Score:** {entry['score']}/10")
                if entry.get("ai_feedback"):
                    st.info(entry["ai_feedback"])
                for tip in entry.get("tips", []):
                    st.caption(f"💡 {tip}")

        st.divider()
        col1, col2 = st.columns(2)
        if col1.button("💾 Save to History"):
            if data_mgr.save(report):
                st.success("Saved!")
            else:
                st.error("Save failed.")
        col2.download_button(
            "⬇ Download Markdown",
            data=report_gen.to_markdown(report),
            file_name=f"report_{name.replace(' ', '_')}.md",
            mime="text/markdown",
        )

# ════════════════════════════════════════════════════════════════
# PAGE: History
# ════════════════════════════════════════════════════════════════
elif "History" in page:
    st.title("📚 History")

    all_reports = data_mgr.load_all()
    if not all_reports:
        st.info("No saved sessions yet. Save a session from the Report tab.")
    else:
        scores = [r.get("average_score", 0) for r in all_reports]
        col1, col2, col3 = st.columns(3)
        col1.metric("Sessions",        len(all_reports))
        col2.metric("All-time Avg",    f"{round(sum(scores)/len(scores), 2)} / 10")
        col3.metric("Total Questions", sum(r.get("questions_attempted", 0) for r in all_reports))

        st.divider()
        for i, rep in enumerate(reversed(all_reports), 1):
            with st.expander(f"Session {i} · {rep.get('candidate')} · {rep.get('started_at')} · Avg {rep.get('average_score')}/10"):
                st.write(f"**Mode:** {rep.get('mode')}  |  **Grade:** {rep.get('overall_grade')}")
                for qtype, sc in rep.get("score_by_type", {}).items():
                    st.write(f"**{qtype}:** {sc}/10")
                    st.progress(sc / 10)

        if st.button("🗑 Clear All History"):
            data_mgr.clear()
            st.success("Cleared.")
            st.rerun()

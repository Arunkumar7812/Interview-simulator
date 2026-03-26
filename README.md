# 🎯 InterviewAI — Smart Interview Simulator

> An AI-powered interview practice tool built with Python OOP + Streamlit. Practice real interview questions across multiple categories and get instant AI feedback on every answer.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit&logoColor=white)
![OOP](https://img.shields.io/badge/Design-OOP-green)
![AI](https://img.shields.io/badge/AI-Claude%20Powered-purple)

---

## 📌 Problem Statement

Job seekers and students preparing for technical and HR interviews often lack access to personalised, real-time feedback on their answers. Existing mock interview tools are either too generic, require a human interviewer, or don't evaluate the quality of answers intelligently.

**InterviewAI** solves this by providing:
- A self-paced interview simulator with real-world questions
- Instant AI-powered scoring and detailed feedback
- Performance tracking across multiple sessions
- Coverage of all major interview categories

---

## ✨ Features

- 🎤 **30+ Questions** across HR, Technical, DSA, Behavioural & System Design
- ⚡ **AI Evaluation** via Claude (Anthropic API) — score, strengths, improvements & ideal points
- 🔄 **Rule-based Fallback** evaluator when no API key is provided
- 📊 **Performance Reports** with score breakdown by category
- 📚 **Session History** saved locally as JSON
- ⬇️ **Export Report** as Markdown file
- 🎯 **Filter by Category & Difficulty** (Easy / Medium / Hard)

---

## 🗂️ Project Structure

```
interview_simulator/
├── app.py          # Streamlit UI (4 pages: Home, Interview, Report, History)
├── model.py        # OOP backend
├── requirements.txt
├── data.json       # Auto-created when sessions are saved
└── README.md
```

---

## 🧩 OOP Design

| Class | Responsibility |
|---|---|
| `Question` | Data model — stores text, type, difficulty, tags |
| `QuestionBank` | 30+ questions; supports type & difficulty filtering |
| `Evaluator` | Rule-based scoring using word count + keyword density |
| `InterviewSession` | Tracks responses, computes per-session stats |
| `ReportGenerator` | Builds structured report dict + Markdown export |
| `DataManager` | Reads/writes session history to `data.json` |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/interview-simulator.git
cd interview-simulator
```

### 2. Install dependencies

```bash
pip install streamlit requests
```

### 3. Run the app

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

> **VS Code users:** Open the folder in VS Code, press `` Ctrl+` `` to open the terminal, then run the command above.

---

## 🤖 AI Evaluation (Optional)

For AI-powered feedback, get a free API key from [console.anthropic.com](https://console.anthropic.com) and paste it in the sidebar toggle inside the app.

**Without an API key**, the app still works using the built-in rule-based evaluator.

**AI evaluation returns:**
- Score (0–10)
- Grade (Excellent / Good / Average / Needs Improvement)
- Strengths — what you did well
- Areas to Improve — specific gaps
- Ideal Points — key concepts you should have mentioned
- Overall Feedback — a holistic 2–3 sentence paragraph

---

## 📸 App Pages

| Page | Description |
|---|---|
| 🏠 Home | Overview, feature list, OOP architecture |
| 🎤 Interview | Answer questions, get instant feedback |
| 📊 Report | Full performance breakdown by category |
| 📚 History | All past saved sessions with all-time stats |

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Streamlit** — UI framework
- **Anthropic Claude API** — AI evaluation
- **JSON** — local data persistence

---

## 📈 Future Improvements

- [ ] Voice input for answers
- [ ] Timer per question
- [ ] Export report as PDF
- [ ] User login & cloud storage
- [ ] More question categories (DBMS, OS, CN)
- [ ] Difficulty auto-adjustment based on performance

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

> Built with ❤️ using Python OOP + Streamlit + Claude AI

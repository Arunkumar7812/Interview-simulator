import random
import json
import os
from datetime import datetime


# ─────────────────────────────────────────────
# 1. Question & QuestionBank
# ─────────────────────────────────────────────

class Question:
    """Represents a single interview question."""

    TYPES = ("HR", "Technical", "DSA", "Behavioural", "System Design")

    def __init__(self, text: str, qtype: str, difficulty: str = "Medium", tags: list = None):
        if qtype not in self.TYPES:
            raise ValueError(f"qtype must be one of {self.TYPES}")
        self.text = text
        self.qtype = qtype
        self.difficulty = difficulty          # Easy / Medium / Hard
        self.tags: list[str] = tags or []

    def __repr__(self):
        return f"<Question [{self.qtype} | {self.difficulty}] {self.text[:40]}...>"


class QuestionBank:
    """Stores and retrieves questions with optional filtering."""

    def __init__(self):
        self._questions: list[Question] = [
            # ── HR ──────────────────────────────────────────────────────────
            Question("Tell me about yourself.", "HR", "Easy", ["intro"]),
            Question("Where do you see yourself in 5 years?", "HR", "Medium", ["career"]),
            Question("What is your greatest weakness?", "HR", "Medium", ["self-awareness"]),
            Question("Why do you want to work here?", "HR", "Easy", ["motivation"]),
            Question("Describe a time you handled a conflict at work.", "HR", "Hard", ["conflict"]),
            Question("What motivates you to perform at your best?", "HR", "Medium", ["motivation"]),
            Question("How do you handle tight deadlines?", "HR", "Medium", ["time-management"]),
            Question("Tell me about a failure and what you learned from it.", "HR", "Hard", ["growth"]),

            # ── Technical ───────────────────────────────────────────────────
            Question("Explain the four pillars of OOP.", "Technical", "Easy", ["oop", "python"]),
            Question("What is the difference between a list and a tuple in Python?", "Technical", "Easy", ["python"]),
            Question("What are Python decorators and how do you use them?", "Technical", "Medium", ["python"]),
            Question("Explain how garbage collection works in Python.", "Technical", "Medium", ["python", "memory"]),
            Question("What is a REST API? Explain HTTP methods.", "Technical", "Easy", ["web", "api"]),
            Question("What is the difference between SQL and NoSQL databases?", "Technical", "Medium", ["databases"]),
            Question("Explain the concept of multithreading vs multiprocessing.", "Technical", "Hard", ["concurrency"]),
            Question("What are design patterns? Name and explain three.", "Technical", "Hard", ["design-patterns"]),
            Question("How does a hash table work internally?", "Technical", "Medium", ["data-structures"]),

            # ── DSA ─────────────────────────────────────────────────────────
            Question("What is Big-O notation? Give examples.", "DSA", "Easy", ["complexity"]),
            Question("Explain the difference between BFS and DFS.", "DSA", "Medium", ["graphs"]),
            Question("How does merge sort work? What is its time complexity?", "DSA", "Medium", ["sorting"]),
            Question("What is a binary search tree? Explain insertion and deletion.", "DSA", "Medium", ["trees"]),
            Question("What is dynamic programming? Give an example problem.", "DSA", "Hard", ["dp"]),
            Question("Explain Dijkstra's algorithm.", "DSA", "Hard", ["graphs", "shortest-path"]),
            Question("How do you detect a cycle in a linked list?", "DSA", "Medium", ["linked-lists"]),
            Question("What is the two-pointer technique? When do you use it?", "DSA", "Medium", ["arrays"]),

            # ── Behavioural ─────────────────────────────────────────────────
            Question("Describe a challenging project you led.", "Behavioural", "Medium", ["leadership"]),
            Question("Tell me about a time you disagreed with your manager.", "Behavioural", "Hard", ["conflict"]),
            Question("Give an example of when you showed initiative.", "Behavioural", "Medium", ["initiative"]),
            Question("How do you prioritise tasks when everything is urgent?", "Behavioural", "Medium", ["prioritisation"]),

            # ── System Design ────────────────────────────────────────────────
            Question("Design a URL shortener like bit.ly.", "System Design", "Hard", ["scalability", "databases"]),
            Question("How would you design Twitter's feed system?", "System Design", "Hard", ["scalability", "caching"]),
            Question("Design a notification system for a large-scale app.", "System Design", "Hard", ["queues", "microservices"]),
            Question("How would you design a rate limiter?", "System Design", "Medium", ["api", "scalability"]),
        ]

    # ── Accessors ────────────────────────────────────────────────────────────

    def get_random(self, qtype: str = None, difficulty: str = None) -> Question:
        pool = self._questions
        if qtype:
            pool = [q for q in pool if q.qtype == qtype]
        if difficulty:
            pool = [q for q in pool if q.difficulty == difficulty]
        if not pool:
            raise ValueError("No questions match the given filters.")
        return random.choice(pool)

    def get_by_type(self, qtype: str) -> list[Question]:
        return [q for q in self._questions if q.qtype == qtype]

    @property
    def all_types(self) -> list[str]:
        return list(Question.TYPES)

    @property
    def all_difficulties(self) -> list[str]:
        return ["Easy", "Medium", "Hard"]

    def __len__(self):
        return len(self._questions)


# ─────────────────────────────────────────────
# 2. Evaluator (rule-based fallback)
# ─────────────────────────────────────────────

class Evaluator:
    """
    Rule-based evaluator with topic relevance detection.
    Penalises answers that don't match the question's domain.
    """

    QUALITY_KEYWORDS = {
        "example", "because", "therefore", "however", "specifically",
        "complexity", "algorithm", "implementation", "trade-off", "advantage",
        "disadvantage", "performance", "scalable", "efficient", "alternatively",
    }

    # Per question-type domain keywords — answer must contain at least one
    DOMAIN_KEYWORDS = {
        "Technical": [
            "python", "code", "function", "class", "object", "variable", "list",
            "tuple", "dict", "array", "loop", "method", "library", "module",
            "stack", "queue", "tree", "graph", "sort", "search", "api", "database",
            "sql", "http", "thread", "memory", "pointer", "compile", "runtime",
            "exception", "inheritance", "polymorphism", "encapsulation", "decorator",
            "iterator", "generator", "lambda", "recursion", "binary", "hash",
        ],
        "DSA": [
            "array", "list", "stack", "queue", "tree", "graph", "heap", "hash",
            "sort", "search", "complexity", "big-o", "o(n)", "o(log", "node",
            "pointer", "linked", "binary", "depth", "breadth", "recursion",
            "dynamic", "greedy", "backtrack", "divide", "conquer", "pivot",
        ],
        "System Design": [
            "server", "database", "cache", "load", "scale", "api", "service",
            "storage", "queue", "message", "cdn", "dns", "http", "rest",
            "microservice", "monolith", "partition", "replica", "consistency",
            "availability", "latency", "throughput", "sharding", "index",
        ],
        "HR": [
            "team", "work", "project", "manager", "goal", "challenge", "skill",
            "experience", "role", "company", "responsibility", "career", "growth",
            "communication", "leadership", "conflict", "deadline", "motivat",
            "collaborate", "feedback", "strength", "weakness", "achieve",
        ],
        "Behavioural": [
            "situation", "task", "action", "result", "team", "challenge",
            "project", "manager", "conflict", "deadline", "initiative",
            "problem", "solution", "decision", "lead", "collaborat", "impact",
        ],
    }

    def evaluate(self, answer: str, question=None) -> dict:
        words     = answer.strip().split()
        word_count = len(words)
        lower     = answer.lower()

        # ── Relevance check ──────────────────────────────────────
        is_irrelevant = False
        if question and question.qtype in self.DOMAIN_KEYWORDS:
            domain_kws = self.DOMAIN_KEYWORDS[question.qtype]
            matched    = [kw for kw in domain_kws if kw in lower]
            if not matched:
                is_irrelevant = True

        # If irrelevant — cap score at 2 immediately
        if is_irrelevant:
            return {
                "score":         1.0,
                "grade":         "Needs Improvement",
                "color":         "#ef4444",
                "word_count":    word_count,
                "is_irrelevant": True,
                "is_incorrect":  True,
                "is_contradictory": False,
                "tips": [
                    "Your answer is completely unrelated to the question.",
                    f"This is a {question.qtype} question — answer using relevant {question.qtype} concepts.",
                    "Read the question carefully before answering.",
                ],
                "ai_powered": False,
            }

        # ── Normal scoring (only reached if relevant) ────────────
        keyword_hits   = sum(1 for kw in self.QUALITY_KEYWORDS if kw in lower)
        has_structure  = any(p in answer for p in ["1.", "2.", "-", "•", "\n"])

        base            = min(word_count / 5, 5)
        kw_bonus        = min(keyword_hits * 0.5, 3)
        structure_bonus = 1.5 if has_structure else 0
        score           = round(min(base + kw_bonus + structure_bonus, 10), 1)

        if score >= 8:
            grade = "Excellent"
        elif score >= 6:
            grade = "Good"
        elif score >= 4:
            grade = "Average"
        else:
            grade = "Needs Improvement"

        tips = []
        if word_count < 20:
            tips.append("Expand your answer with more detail.")
        if keyword_hits == 0:
            tips.append("Include domain-specific terminology.")
        if not has_structure:
            tips.append("Structure your answer with numbered points or bullet points.")

        return {
            "score":            score,
            "grade":            grade,
            "color":            "#22c55e" if score >= 8 else "#84cc16" if score >= 6 else "#f59e0b" if score >= 4 else "#ef4444",
            "word_count":       word_count,
            "is_irrelevant":    False,
            "is_incorrect":     False,
            "is_contradictory": False,
            "tips":             tips,
            "ai_powered":       False,
        }


# ─────────────────────────────────────────────
# 3. InterviewSession
# ─────────────────────────────────────────────

class InterviewSession:
    """Manages one interview session (questions asked + responses)."""

    def __init__(self, candidate_name: str = "Candidate", mode: str = "Mixed"):
        self.candidate_name = candidate_name
        self.mode = mode                          # Mixed / Focused (single type)
        self.started_at = datetime.now()
        self._history: list[dict] = []
        self._question_count = 0

    def record(self, question: Question, answer: str, evaluation: dict) -> None:
        self._question_count += 1
        self._history.append({
            "index": self._question_count,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": question.qtype,
            "difficulty": question.difficulty,
            "question": question.text,
            "answer": answer,
            "score": evaluation["score"],
            "grade": evaluation["grade"],
            "tips": evaluation.get("tips", []),
            "ai_feedback": evaluation.get("ai_feedback", ""),
            "ai_powered": evaluation.get("ai_powered", False),
        })

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    @property
    def total_score(self) -> float:
        if not self._history:
            return 0.0
        return round(sum(r["score"] for r in self._history) / len(self._history), 2)

    @property
    def question_count(self) -> int:
        return self._question_count

    def score_by_type(self) -> dict[str, float]:
        result = {}
        for entry in self._history:
            t = entry["type"]
            result.setdefault(t, []).append(entry["score"])
        return {t: round(sum(scores) / len(scores), 2) for t, scores in result.items()}

    def is_empty(self) -> bool:
        return len(self._history) == 0


# ─────────────────────────────────────────────
# 4. ReportGenerator
# ─────────────────────────────────────────────

class ReportGenerator:
    """Generates a structured performance report from a session."""

    GRADE_THRESHOLDS = [
        (9, "Outstanding 🏆"),
        (7, "Strong Candidate ⭐"),
        (5, "Promising 📈"),
        (3, "Needs Work 🔧"),
        (0, "Significant Improvement Needed 📚"),
    ]

    def generate(self, session: InterviewSession) -> dict:
        if session.is_empty():
            return {}

        avg = session.total_score
        overall_grade = next(label for threshold, label in self.GRADE_THRESHOLDS if avg >= threshold)
        by_type = session.score_by_type()

        strengths = [t for t, s in by_type.items() if s >= 7]
        weak_areas = [t for t, s in by_type.items() if s < 5]

        return {
            "candidate": session.candidate_name,
            "mode": session.mode,
            "started_at": session.started_at.strftime("%Y-%m-%d %H:%M"),
            "questions_attempted": session.question_count,
            "average_score": avg,
            "overall_grade": overall_grade,
            "score_by_type": by_type,
            "strengths": strengths,
            "weak_areas": weak_areas,
            "responses": session.history,
        }

    def to_markdown(self, report: dict) -> str:
        if not report:
            return "No data available."
        lines = [
            f"# Interview Report – {report['candidate']}",
            f"**Date:** {report['started_at']}  |  **Mode:** {report['mode']}",
            f"**Questions Attempted:** {report['questions_attempted']}",
            f"**Average Score:** {report['average_score']} / 10",
            f"**Overall Grade:** {report['overall_grade']}",
            "",
            "## Score by Category",
        ]
        for qtype, score in report["score_by_type"].items():
            bar = "█" * int(score) + "░" * (10 - int(score))
            lines.append(f"- **{qtype}**: {bar}  {score}/10")
        if report["strengths"]:
            lines += ["", f"**Strengths:** {', '.join(report['strengths'])}"]
        if report["weak_areas"]:
            lines += [f"**Focus Areas:** {', '.join(report['weak_areas'])}"]
        return "\n".join(lines)


# ─────────────────────────────────────────────
# 5. DataManager
# ─────────────────────────────────────────────

class DataManager:
    """Handles persistence of session reports to JSON."""

    def __init__(self, filepath: str = "data.json"):
        self.filepath = filepath

    def save(self, report: dict) -> bool:
        try:
            existing = self.load_all()
            existing.append(report)
            with open(self.filepath, "w") as f:
                json.dump(existing, f, indent=2)
            return True
        except Exception:
            return False

    def load_all(self) -> list[dict]:
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath) as f:
                data = json.load(f)
            return data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, IOError):
            return []

    def clear(self) -> None:
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

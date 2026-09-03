# 🧠 AI Quiz Master

A Streamlit app that generates quizzes on any topic with AI, times you, explains
your mistakes, turns wrong answers into flashcards, and tracks your progress.

## Features
- **Login / Register** — simple SQLite-backed accounts (`auth.py`, PBKDF2-hashed passwords)
- **AI-generated quizzes** — pick a topic, difficulty, number of questions, and total time
- **Countdown timer** — auto-submits when time runs out
- **AI explanations** — every wrong answer gets a short AI-written explanation
- **Auto flashcards** — wrong answers become flashcards you can review/delete later
- **History** — every past quiz with score, time, and per-question review
- **CSV export** — export a single quiz or your entire question history
- **Study analysis** — accuracy by topic, weakest topic, score trend over time

## Files
```
app.py            # Streamlit UI + AI calls + quiz flow
auth.py            # registration / login / session handling
database.py        # SQLite schema + all queries
.env               # your GROQ_API_KEY (and optional model override)
requirements.txt    # dependencies
```

## Setup
   
1. Run the app:
   ```bash
   streamlit run app.py
   ```

A `quiz_master.db` SQLite file is created automatically on first run — no setup needed.

## Notes
- If `streamlit-autorefresh` isn't installed, the timer still works but only
  updates when you interact with the page (select an answer, etc.) instead of
  ticking every second.
- Delete `quiz_master.db` any time to reset all data.
-
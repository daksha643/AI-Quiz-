import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_file="quiz_master.db"):
        self.db_file = db_file
        self._create_tables()
    
    def _create_tables(self):
        """Create all necessary tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quizzes_taken INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                total_time INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Quiz history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage REAL NOT NULL,
                duration INTEGER NOT NULL,
                avg_time_per_question REAL DEFAULT 0,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Wrong questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wrong_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                user_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                time_taken REAL DEFAULT 0,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Saved quizzes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                questions TEXT NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Flashcards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                difficulty INTEGER DEFAULT 1,
                next_review DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Study sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                time_spent INTEGER DEFAULT 0,
                topics TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============ USER METHODS ============
    
    def get_user_id(self, username: str) -> Optional[int]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def create_user(self, username: str, password_hash: str, email: str = "") -> bool:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            user_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO user_stats (user_id) VALUES (?)",
                (user_id,)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, email, created_at FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "password": result[2],
                "email": result[3],
                "created_at": result[4]
            }
        return None
    
    # ============ STATS METHODS ============
    
    def update_stats(self, user_id: int, score: int, total: int, time_taken: int = 0):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_stats 
            SET quizzes_taken = quizzes_taken + 1,
                total_score = total_score + ?,
                total_questions = total_questions + ?,
                total_time = total_time + ?
            WHERE user_id = ?
        ''', (score, total, time_taken, user_id))
        conn.commit()
        conn.close()
    
    def get_stats(self, user_id: int) -> Dict:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT quizzes_taken, total_score, total_questions, total_time FROM user_stats WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "quizzes_taken": result[0],
                "total_score": result[1],
                "total_questions": result[2],
                "total_time": result[3]
            }
        return {"quizzes_taken": 0, "total_score": 0, "total_questions": 0, "total_time": 0}
    
    # ============ QUIZ HISTORY METHODS ============
    
    def save_quiz_history(self, user_id: int, data: Dict):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quiz_history 
            (user_id, topic, difficulty, score, total_questions, percentage, duration, avg_time_per_question)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['topic'],
            data['difficulty'],
            data['score'],
            data['total'],
            data['percentage'],
            data['duration'],
            data.get('avg_time', 0)
        ))
        conn.commit()
        conn.close()
    
    def get_quiz_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT topic, difficulty, score, total_questions, percentage, duration, avg_time_per_question, date
            FROM quiz_history
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "topic": r[0],
                "difficulty": r[1],
                "score": r[2],
                "total": r[3],
                "percentage": r[4],
                "duration": r[5],
                "avg_time": r[6],
                "date": r[7]
            }
            for r in results
        ]
    
    # ============ WRONG QUESTIONS METHODS ============
    
    def save_wrong_question(self, user_id: int, data: Dict):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wrong_questions 
            (user_id, topic, question, correct_answer, user_answer, explanation, time_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['topic'],
            data['question'],
            data['correct_answer'],
            data['user_answer'],
            data['explanation'],
            data.get('time_taken', 0)
        ))
        conn.commit()
        conn.close()
    
    def get_wrong_questions(self, user_id: int, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, topic, question, correct_answer, user_answer, explanation, time_taken, date
            FROM wrong_questions
            WHERE user_id = ? AND reviewed = 0
            ORDER BY date DESC
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "topic": r[1],
                "question": r[2],
                "correct_answer": r[3],
                "user_answer": r[4],
                "explanation": r[5],
                "time_taken": r[6],
                "date": r[7]
            }
            for r in results
        ]
    
    def mark_question_reviewed(self, question_id: int):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE wrong_questions SET reviewed = 1 WHERE id = ?",
            (question_id,)
        )
        conn.commit()
        conn.close()
    
    def clear_wrong_questions(self, user_id: int):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM wrong_questions WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        conn.close()
    
    # ============ SAVED QUIZZES METHODS ============
    
    def save_quiz(self, user_id: int, topic: str, difficulty: str, questions: List[Dict]):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO saved_quizzes (user_id, topic, difficulty, questions)
            VALUES (?, ?, ?, ?)
        ''', (user_id, topic, difficulty, json.dumps(questions)))
        conn.commit()
        conn.close()
    
    def get_saved_quizzes(self, user_id: int, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, topic, difficulty, date, questions
            FROM saved_quizzes
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "topic": r[1],
                "difficulty": r[2],
                "date": r[3],
                "questions": json.loads(r[4])
            }
            for r in results
        ]
    
    # ============ FLASHCARD METHODS ============
    
    def save_flashcard(self, user_id: int, data: Dict):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO flashcards 
            (user_id, topic, question, correct_answer, explanation, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['topic'],
            data['question'],
            data['correct_answer'],
            data['explanation'],
            1
        ))
        conn.commit()
        conn.close()
    
    def get_flashcards(self, user_id: int, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, topic, question, correct_answer, explanation, difficulty
            FROM flashcards
            WHERE user_id = ?
            ORDER BY difficulty ASC, created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "topic": r[1],
                "question": r[2],
                "correct_answer": r[3],
                "explanation": r[4],
                "difficulty": r[5]
            }
            for r in results
        ]
    
    def update_flashcard_difficulty(self, flashcard_id: int, difficulty: int):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE flashcards SET difficulty = ? WHERE id = ?",
            (difficulty, flashcard_id)
        )
        conn.commit()
        conn.close()
    
    # ============ STUDY ANALYTICS METHODS ============
    
    def save_study_session(self, user_id: int, data: Dict):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO study_sessions 
            (user_id, date, total_questions, correct_answers, time_spent, topics)
            VALUES (?, DATE('now'), ?, ?, ?, ?)
        ''', (
            user_id,
            data['total_questions'],
            data['correct_answers'],
            data['time_spent'],
            data['topics']
        ))
        conn.commit()
        conn.close()
    
    def get_study_analytics(self, user_id: int, days: int = 30) -> Dict:
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, total_questions, correct_answers, time_spent
            FROM study_sessions
            WHERE user_id = ? AND date >= DATE('now', ?)
            ORDER BY date DESC
        ''', (user_id, f'-{days} days'))
        daily_stats = cursor.fetchall()
        
        cursor.execute('''
            SELECT topic, 
                   COUNT(*) as total,
                   SUM(CASE WHEN reviewed = 0 THEN 1 ELSE 0 END) as pending,
                   AVG(time_taken) as avg_time
            FROM wrong_questions
            WHERE user_id = ?
            GROUP BY topic
        ''', (user_id,))
        topic_stats = cursor.fetchall()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_quizzes,
                SUM(total_questions) as total_questions,
                SUM(score) as total_correct,
                SUM(duration) as total_time
            FROM quiz_history
            WHERE user_id = ?
        ''', (user_id,))
        overall = cursor.fetchone()
        
        conn.close()
        
        return {
            "daily": [
                {"date": r[0], "total": r[1], "correct": r[2], "time": r[3]}
                for r in daily_stats
            ],
            "topics": [
                {"topic": r[0], "total": r[1], "pending": r[2], "avg_time": round(r[3] if r[3] else 0, 1)}
                for r in topic_stats
            ],
            "overall": {
                "total_quizzes": overall[0] if overall else 0,
                "total_questions": overall[1] if overall else 0,
                "total_correct": overall[2] if overall else 0,
                "total_time": overall[3] if overall else 0
            }
        }
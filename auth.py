import bcrypt
from typing import List, Dict
from database import Database

class AuthManager:
    def __init__(self):
        self.db = Database()
    
    # ============ AUTHENTICATION ============
    
    def register_user(self, username: str, password: str, email: str = "") -> bool:
        if self.db.get_user(username):
            return False
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return self.db.create_user(username, hashed.decode('utf-8'), email)
    
    def login_user(self, username: str, password: str) -> bool:
        user = self.db.get_user(username)
        if not user:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
    
    def get_user_id(self, username: str) -> int:
        user = self.db.get_user(username)
        return user['id'] if user else None
    
    # ============ STATS ============
    
    def update_stats(self, username: str, score: int, total: int, time_taken: int = 0):
        user = self.db.get_user(username)
        if user:
            self.db.update_stats(user['id'], score, total, time_taken)
    
    def get_user_stats(self, username: str):
        user = self.db.get_user(username)
        if user:
            return self.db.get_stats(user['id'])
        return None
    
    # ============ QUIZ HISTORY ============
    
    def save_quiz_history(self, username: str, data: Dict):
        user = self.db.get_user(username)
        if user:
            self.db.save_quiz_history(user['id'], data)
    
    def get_quiz_history(self, username: str, limit: int = 50) -> List[Dict]:
        user = self.db.get_user(username)
        if user:
            return self.db.get_quiz_history(user['id'], limit)
        return []
    
    # ============ WRONG QUESTIONS ============
    
    def save_wrong_question(self, username: str, data: Dict):
        user = self.db.get_user(username)
        if user:
            self.db.save_wrong_question(user['id'], data)
    
    def get_wrong_questions(self, username: str, limit: int = 20) -> List[Dict]:
        user = self.db.get_user(username)
        if user:
            return self.db.get_wrong_questions(user['id'], limit)
        return []
    
    def mark_question_reviewed(self, username: str, question_id: int):
        user = self.db.get_user(username)
        if user:
            self.db.mark_question_reviewed(question_id)
    
    def clear_wrong_questions(self, username: str):
        user = self.db.get_user(username)
        if user:
            self.db.clear_wrong_questions(user['id'])
    
    # ============ SAVED QUIZZES ============
    
    def save_quiz(self, username: str, topic: str, difficulty: str, questions: List[Dict]):
        user = self.db.get_user(username)
        if user:
            self.db.save_quiz(user['id'], topic, difficulty, questions)
    
    def get_saved_quizzes(self, username: str, limit: int = 10) -> List[Dict]:
        user = self.db.get_user(username)
        if user:
            return self.db.get_saved_quizzes(user['id'], limit)
        return []
    
    # ============ FLASHCARDS ============
    
    def save_flashcard(self, username: str, data: Dict):
        user = self.db.get_user(username)
        if user:
            self.db.save_flashcard(user['id'], data)
    
    def get_flashcards(self, username: str, limit: int = 20) -> List[Dict]:
        user = self.db.get_user(username)
        if user:
            return self.db.get_flashcards(user['id'], limit)
        return []
    
    def update_flashcard_difficulty(self, flashcard_id: int, difficulty: int):
        self.db.update_flashcard_difficulty(flashcard_id, difficulty)
    
    # ============ STUDY ANALYTICS ============
    
    def save_study_session(self, username: str, data: Dict):
        user = self.db.get_user(username)
        if user:
            self.db.save_study_session(user['id'], data)
    
    def get_study_analytics(self, username: str, days: int = 30) -> Dict:
        user = self.db.get_user(username)
        if user:
            return self.db.get_study_analytics(user['id'], days)
        return {"daily": [], "topics": [], "overall": {"total_quizzes": 0, "total_questions": 0, "total_correct": 0, "total_time": 0}}
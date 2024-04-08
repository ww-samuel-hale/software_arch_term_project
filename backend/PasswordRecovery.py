import sqlite3
from werkzeug.security import check_password_hash
from Db import get_db_connection

class Handler:
    def set_next(self, handler):
        pass

    def handle(self, request):
        pass

class SecurityQuestionHandler(Handler):
    def __init__(self, question, answer_hash):
        self.question = question
        self.answer_hash = answer_hash
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler

    def handle(self, provided_answer):
        if check_password_hash(self.answer_hash, provided_answer):
            if self.next_handler is not None:
                return self.next_handler.handle(provided_answer)
            return True  # All questions were answered correctly
        return False  # Incorrect answer

class PasswordRecoveryChain:
    def __init__(self, user_id):
        self.head_handler = None
        self.user_id = user_id

    def setup_chain(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Question, Answer FROM SecurityQuestions WHERE UserID = ?', (self.user_id,))
        questions_and_answers = cursor.fetchall()

        previous_handler = None
        for qa in questions_and_answers:
            current_handler = SecurityQuestionHandler(qa['Question'], qa['Answer'])
            if previous_handler:
                previous_handler.set_next(current_handler)
            else:
                self.head_handler = current_handler
            previous_handler = current_handler
        conn.close()

    def verify_answers(self, provided_answers):
        current_handler = self.head_handler
        for answer in provided_answers:
            if not current_handler or not current_handler.handle(answer):
                return False  # Stop at the first incorrect answer
            current_handler = current_handler.next_handler
        return True  # All answers were correct

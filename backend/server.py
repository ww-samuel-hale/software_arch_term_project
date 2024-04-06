import sqlite3
from flask import Flask, request, session, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_urlsafe(16)  # Set a secret key for sessions

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def db_initialization():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                          UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                          Email TEXT NOT NULL UNIQUE,
                          Password TEXT NOT NULL
                      )''')

    # Create SecurityQuestions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS SecurityQuestions (
                          QuestionID INTEGER PRIMARY KEY AUTOINCREMENT,
                          UserID INTEGER,
                          Question TEXT NOT NULL,
                          Answer TEXT NOT NULL,
                          FOREIGN KEY (UserID) REFERENCES Users (UserID)
                      )''')

    # Create CarListing table
    cursor.execute('''CREATE TABLE IF NOT EXISTS CarListing (
                          ListingID INTEGER PRIMARY KEY AUTOINCREMENT,
                          OwnerID INTEGER,
                          Model TEXT NOT NULL,
                          Year INTEGER NOT NULL,
                          Mileage INTEGER NOT NULL,
                          PickUpLocation TEXT NOT NULL,
                          RentalPricing REAL NOT NULL,
                          FOREIGN KEY (OwnerID) REFERENCES Users (UserID)
                      )''')

    # Create Bookings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Bookings (
                          BookingID INTEGER PRIMARY KEY AUTOINCREMENT,
                          ListingID INTEGER,
                          RenterID INTEGER,
                          StartDate TEXT NOT NULL,
                          EndDate TEXT NOT NULL,
                          FOREIGN KEY (ListingID) REFERENCES CarListing (ListingID),
                          FOREIGN KEY (RenterID) REFERENCES Users (UserID)
                      )''')

    # Create Payments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Payments (
                          PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
                          BookingID INTEGER,
                          Amount REAL NOT NULL,
                          Status TEXT NOT NULL,
                          FOREIGN KEY (BookingID) REFERENCES Bookings (BookingID)
                      )''')

    conn.commit()
    conn.close()

class User:
    def __init__(self, email, password, security_questions):
        self.email = email
        self.password = generate_password_hash(password)
        self.security_questions = security_questions

    def save_to_db(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the email already exists
        cursor.execute('SELECT * FROM Users WHERE Email = ?', (self.email,))
        if cursor.fetchone():
            conn.close()
            return 'email_exists'

        try:
            # Proceed with user registration
            cursor.execute('INSERT INTO Users (Email, Password) VALUES (?, ?)', (self.email, self.password))
            user_id = cursor.lastrowid

            for question in self.security_questions:
                cursor.execute('INSERT INTO SecurityQuestions (UserID, Question, Answer) VALUES (?, ?, ?)',
                               (user_id, question['question'], generate_password_hash(question['answer'])))

            conn.commit()
            return 'registration_successful'

        except sqlite3.IntegrityError:
            conn.rollback()
            return 'integrity_error'

        finally:
            conn.close()

    @staticmethod
    def authenticate(email, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['Password'], password):
            return user
        else:
            return None

class SecurityQuestion:
    def __init__(self, question, answer):
        self.question = question
        self.answer = generate_password_hash(answer)

class UserSession:
    _session_instance = None

    @classmethod
    def get_instance(cls):
        if not cls._session_instance:
            cls._session_instance = cls()
        return cls._session_instance

    def login(self, user):
        session['user_id'] = user['UserID']
        session['email'] = user['Email']

    def logout(self):
        session.pop('user_id', None)
        session.pop('email', None)

# Wrapper to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to login page, or return error
            return 'Unauthorized', 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(data['email'], data['password'], data['security_questions'])

    save_status = user.save_to_db()

    if save_status == 'email_exists':
        return 'Email already registered', 409
    elif save_status == 'registration_successful':
        return 'Registered successfully', 201
    else:
        return 'Registration failed due to a database error', 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.authenticate(data['email'], data['password'])
    if user:
        UserSession.get_instance().login(user)
        return 'Logged in successfully'
    else:
        return 'Login failed', 401

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    UserSession.get_instance().logout()
    return 'Logged out successfully'

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    db_initialization()  # Initialize the database tables
    app.run(debug=True)

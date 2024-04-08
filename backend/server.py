import sqlite3
from flask import Flask, request, session, g, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
from Builder import ConcreteCarListingBuilder, CarDirector
from Db import get_db_connection, db_initialization
from Observer import BookingManager, Observer


app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_urlsafe(16)  # Set a secret key for sessions


### AUTHENTICATION SINGLETONS ###
class User(Observer):
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
            
    def update(self, subject, message, related_id):
        user_id = message['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Notifications (UserID, Message, RelatedEntityID)
            VALUES (?, ?)
        ''', (self.user_id, message, related_id))
        conn.commit()
        conn.close()

    @staticmethod
    def authenticate(email, password):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE Email = ?', (email,))
            user = cursor.fetchone()

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

def get_current_user():
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE UserID = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        return user
    else:
        return None


### AUTHENTICATION ENDPOINTS ###
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
        return 'Logged in successfully', 200
    else:
        return 'Login failed', 401

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    UserSession.get_instance().logout()
    return 'Logged out successfully'

### CAR LISTING ENDPOINTS ###
@app.route('/create-listing', methods=['POST'])
@login_required
def create_listing():
    data = request.json
    builder = ConcreteCarListingBuilder()
    director = CarDirector(builder)

    # Build the car listing
    car_listing = director.construct_car(data)

    # Save the car listing to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO CarListing (OwnerID, Model, Year, Mileage, PickUpLocation, RentalPricing) VALUES (?, ?, ?, ?, ?, ?)',
        (session['user_id'], car_listing.model, car_listing.year, car_listing.mileage, car_listing.pickup_location, car_listing.rental_pricing)
    )
    listing_id = cursor.lastrowid  # Get the ID of the newly created listing

    # Insert availability data
    for availability in data['availability']:
        cursor.execute(
            'INSERT INTO Availability (ListingID, StartDate, EndDate) VALUES (?, ?, ?)',
            (listing_id, availability['start_date'], availability['end_date'])
        )
        
    conn.commit()
    conn.close()

    return jsonify({'message': 'Car listing created successfully'}), 201

@app.route('/update-price/<int:listing_id>', methods=['PUT'])
@login_required
def update_price(listing_id):
    data = request.json
    new_price = data['rental_pricing']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Authenticate the owner of the car listing
    cursor.execute('SELECT OwnerID FROM CarListing WHERE ListingID = ?', (listing_id,))
    car_listing = cursor.fetchone()

    if car_listing and car_listing['OwnerID'] == session['user_id']:
        cursor.execute(
            'UPDATE CarListing SET RentalPricing = ? WHERE ListingID = ?',
            (new_price, listing_id)
        )
        conn.commit()
        message = 'Price updated successfully'
        status_code = 200
    else:
        message = 'Unauthorized or listing not found'
        status_code = 401

    conn.close()
    return jsonify({'message': message}), status_code

@app.route('/update-availability/<int:listing_id>', methods=['PUT'])
@login_required
def update_availability(listing_id):
    data = request.json
    new_availability = data['availability']  # A list of date ranges

    conn = get_db_connection()
    cursor = conn.cursor()

    # Authenticate the owner of the car listing
    cursor.execute('SELECT OwnerID FROM CarListing WHERE ListingID = ?', (listing_id,))
    car_listing = cursor.fetchone()

    if car_listing and car_listing['OwnerID'] == session['user_id']:
        # Remove existing availability
        cursor.execute('DELETE FROM Availability WHERE ListingID = ?', (listing_id,))

        # Insert new availability data
        for availability in new_availability:
            cursor.execute(
                'INSERT INTO Availability (ListingID, StartDate, EndDate) VALUES (?, ?, ?)',
                (listing_id, availability['start_date'], availability['end_date'])
            )

        conn.commit()
        message = 'Availability updated successfully'
        status_code = 200
    else:
        message = 'Unauthorized or listing not found'
        status_code = 401

    conn.close()
    return jsonify({'message': message}), status_code

### BOOKING ENDPOINTS ###
@app.route('/create-booking', methods=['POST'])
@login_required
def create_booking_endpoint():
    data = request.json
    booking_details = {
        'listing_id': data['listing_id'],
        'renter_id': session['user_id'],  # Assuming session['user_id'] holds the ID of the logged-in user
        'start_date': data['start_date'],
        'end_date': data['end_date']
    }
    booking_manager = BookingManager()
    user_details = get_current_user()
    current_user = User(user_details['Email'], '', [])
    booking_manager.attach(current_user)
    booking_id = booking_manager.create_booking(booking_details)
    if booking_id:
        return jsonify({'message': 'Booking created successfully', 'booking_id': booking_id}), 201
    else:
        return jsonify({'message': 'Booking creation failed'}), 500
    
@app.route('/respond-to-booking', methods=['POST'])
@login_required
def respond_to_booking():
    data = request.json
    booking_id = data['booking_id']
    response = data['response']

    booking_manager = BookingManager()
    user_details = get_current_user()
    current_user = User(user_details['Email'], '', [])
    booking_manager.attach(current_user)
    if response == 'accept':
        success = booking_manager.approve_booking(booking_id)
    elif response == 'reject':
        success = booking_manager.reject_booking(booking_id)
    booking_manager.detach(current_user)
    if success:
        return jsonify({'message': 'Booking response recorded successfully'}), 200
    else:
        return jsonify({'message': 'Booking response failed'}), 500

@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking_endpoint(booking_id):
    booking_manager = BookingManager()
    user_details = get_current_user()
    current_user = User(user_details['Email'], '', [])
    booking_manager.attach(current_user)
    success = booking_manager.cancel_booking(booking_id)
    booking_manager.detach(current_user)
    if success:
        return jsonify({'message': 'Booking cancelled successfully'}), 200
    else:
        return jsonify({'message': 'Booking cancellation failed'}), 500

### SEARCH ENDPOINTS ###
@app.route('/filter-listings', methods=['POST'])
@login_required
def filter_listings():
    data = request.json  # This is the user input from the front end
    
    # Get the user_id from session
    user_id = session['user_id']

    # Start with a base query
    query = """
    SELECT cl.*
    FROM CarListing cl
    INNER JOIN Availability a ON cl.ListingID = a.ListingID
    WHERE cl.OwnerID != ?
    """

    # Parameters list to safely pass values into the query
    params = [user_id]

    # Apply filters based on user input
    if 'model' in data:
        query += " AND cl.Model LIKE ?"
        params.append("%{}%".format(data['model']))
    if 'pickup_location' in data:
        query += " AND cl.PickUpLocation LIKE ?"
        params.append("%{}%".format(data['pickup_location']))
    if 'year' in data and 'year_comparator' in data:
        query += " AND cl.Year {} ?".format(data['year_comparator'])
        params.append(data['year'])
    if 'mileage' in data and 'mileage_comparator' in data:
        query += " AND cl.Mileage {} ?".format(data['mileage_comparator'])
        params.append(data['mileage'])
    if 'rental_pricing' in data and 'pricing_comparator' in data:
        query += " AND cl.RentalPricing {} ?".format(data['pricing_comparator'])
        params.append(data['rental_pricing'])
    if 'class' in data:
        query += " AND cl.Class = ?"
        params.append(data['class'])
    if 'from_date' in data and 'to_date' in data:
        query += " AND a.StartDate <= ? AND a.EndDate >= ?"
        params.append(data['from_date'])
        params.append(data['to_date'])
        
    # Execute the query
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    listings = cursor.fetchall()
    conn.close()

    # Convert fetched rows into a list of dictionaries
    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in listings]

    # Return the results
    return jsonify(results)


@app.route('/search-available-cars', methods=['POST'])
def search_available_cars():
    data = request.json  # Expecting 'pickup_location', 'from_date', 'to_date'
    pickup_location = data['pickup_location']
    from_date = data['from_date']
    to_date = data['to_date']
    
    user_id = session['user_id']

    # The SQL query checks for cars that are available within the specified date range
    query = """
    SELECT cl.*
    FROM CarListing cl
    JOIN Availability a ON cl.ListingID = a.ListingID
    WHERE cl.PickUpLocation LIKE ? AND NOT (
        a.StartDate > ? OR
        a.EndDate < ?
    ) AND cl.OwnerID != ?
    """
    pickup_location = f'%{pickup_location}%'
    # Execute the query with parameter substitution to prevent SQL injection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (pickup_location, to_date, from_date, user_id))
    available_cars = cursor.fetchall()
    conn.close()

    # Convert query results into a list of dictionaries to jsonify the response
    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns, row)) for row in available_cars]

    return jsonify(result)

### MESSAGING ENDPOINTS ###
@app.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Conversations
        WHERE Participant1ID = ? OR Participant2ID = ?
    ''', (user_id, user_id))
    conversations = cursor.fetchall()
    conn.close()
    return jsonify(conversations)


@app.route('/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_messages(conversation_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Validate that the user is part of the conversation
    cursor.execute('''
        SELECT * FROM Conversations
        WHERE ConversationID = ? AND (Participant1ID = ? OR Participant2ID = ?)
    ''', (conversation_id, user_id, user_id))
    conversation = cursor.fetchone()
    if not conversation:
        conn.close()
        return 'Unauthorized', 403
    
    cursor.execute('''
        SELECT * FROM Messages WHERE ConversationID = ?
    ''', (conversation_id,))
    messages = cursor.fetchall()
    conn.close()
    return jsonify(messages)


@app.route('/conversations/<int:conversation_id>', methods=['POST'])
@login_required
def send_message(conversation_id):
    user_id = session['user_id']
    content = request.json.get('content')

    if not content:
        return 'No message content provided', 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Validate that the user is part of the conversation
    cursor.execute('''
        SELECT * FROM Conversations
        WHERE ConversationID = ? AND (Participant1ID = ? OR Participant2ID = ?)
    ''', (conversation_id, user_id, user_id))
    conversation = cursor.fetchone()
    if not conversation:
        conn.close()
        return 'Unauthorized', 403

    cursor.execute('''
        INSERT INTO Messages (ConversationID, SenderID, Content)
        VALUES (?, ?, ?)
    ''', (conversation_id, user_id, content))
    conn.commit()
    conn.close()
    return 'Message sent', 200

@app.route('/start-conversation', methods=['POST'])
@login_required
def start_conversation():
    # User ID of the person initiating the conversation (the renter)
    renter_id = session['user_id']
    # Get owner ID from the request to start a conversation with
    data = request.json
    owner_id = data.get('owner_id')

    if not owner_id:
        return 'Owner ID must be provided', 400

    # Avoid creating duplicate conversations between the same two people
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM Conversations
        WHERE (Participant1ID = ? AND Participant2ID = ?) OR (Participant1ID = ? AND Participant2ID = ?)
    ''', (renter_id, owner_id, owner_id, renter_id))
    
    existing_conversation = cursor.fetchone()
    
    # If a conversation already exists, return its ID
    if existing_conversation:
        conn.close()
        return jsonify({'conversation_id': existing_conversation['ConversationID']}), 200

    # If not, create a new conversation
    cursor.execute('''
        INSERT INTO Conversations (Participant1ID, Participant2ID)
        VALUES (?, ?)
    ''', (renter_id, owner_id))

    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'conversation_id': conversation_id}), 201

### NOTIFICATION ENDPOINTS ###
@app.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Notifications WHERE UserID = ? AND Acknowledged = 0', (user_id,))
    notifications = cursor.fetchall()
    conn.close()
    return jsonify(notifications)

@app.route('/notifications/<int:notification_id>', methods=['PUT'])
@login_required
def acknowledge_notification(notification_id):
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Notifications
        SET Acknowledged = 1
        WHERE NotificationID = ? AND UserID = ?
    ''', (notification_id, user_id))
    conn.commit()
    conn.close()
    return 'Notification acknowledged', 200


if __name__ == '__main__':
    db_initialization()  # Initialize the database tables
    app.run(debug=True)

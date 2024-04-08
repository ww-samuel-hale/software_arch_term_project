### DATABASE CONNECTION AND INITIALIZATION ###
import sqlite3

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
                          Password TEXT NOT NULL,
                          WalletBalance REAL DEFAULT 0
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
                          Class TEXT,
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
    
    # Create AvailabilityCalendar table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Availability (
                        AvailabilityID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ListingID INTEGER,
                        StartDate TEXT NOT NULL,
                        EndDate TEXT NOT NULL,
                        FOREIGN KEY (ListingID) REFERENCES CarListing (ListingID)
            )''')
    
    # Create Conversations table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Conversations (
                          ConversationID INTEGER PRIMARY KEY AUTOINCREMENT,
                          Participant1ID INTEGER NOT NULL,
                          Participant2ID INTEGER NOT NULL,
                          FOREIGN KEY (Participant1ID) REFERENCES Users(UserID),
                          FOREIGN KEY (Participant2ID) REFERENCES Users(UserID)
                      )''')

    # Create Messages table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Messages (
                          MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
                          ConversationID INTEGER NOT NULL,
                          SenderID INTEGER NOT NULL,
                          Content TEXT NOT NULL,
                          Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (ConversationID) REFERENCES Conversations(ConversationID),
                          FOREIGN KEY (SenderID) REFERENCES Users(UserID)
                      )''')
    
    # Create Notifications table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Notifications (
                        NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
                        UserID INTEGER NOT NULL,
                        Message TEXT NOT NULL,
                        Acknowledged INTEGER DEFAULT 0,
                        RelatedEntityID INTEGER,
                        FOREIGN KEY (UserID) REFERENCES Users(UserID)
                    )
                    ''')
    
    # Create Booking Requests table
    cursor.execute('''CREATE TABLE IF NOT EXISTS BookingRequests (
                        RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ListingID INTEGER NOT NULL,
                        RequesterID INTEGER NOT NULL,
                        StartDate TEXT NOT NULL,
                        EndDate TEXT NOT NULL,
                        Status TEXT NOT NULL,
                        FOREIGN KEY (ListingID) REFERENCES CarListing(ListingID),
                        FOREIGN KEY (RequesterID) REFERENCES Users(UserID)
                    )
                    ''')
    
    # Create Payments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Payments (
                        PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
                        BookingID INTEGER,
                        UserID INTEGER,
                        Amount REAL NOT NULL,
                        Status TEXT NOT NULL, 
                        TransactionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PaymentMethod TEXT,
                        FOREIGN KEY (BookingID) REFERENCES BookingRequests(RequestID),
                        FOREIGN KEY (UserID) REFERENCES Users(UserID)
                    )
                    ''')
    conn.commit()
    conn.close()

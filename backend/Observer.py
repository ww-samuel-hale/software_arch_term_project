from Db import get_db_connection
import sqlite3
from datetime import datetime, timedelta 

class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, message, related_id, booking_request=None):
        for observer in self._observers:
            observer.update(self, message, related_id, booking_request)

class Observer:
    def update(self, subject, message, related_id, booking_request=None):
        pass

class BookingManager(Subject):
    def update_car_availability(self, conn, listing_id, start_date, end_date):
        cursor = conn.cursor()
        try:
            # Fetch all availability records that overlap with the booking period
            cursor.execute('''
                SELECT AvailabilityID, StartDate, EndDate FROM Availability
                WHERE ListingID = ? AND NOT (StartDate > ? OR EndDate < ?)
            ''', (listing_id, end_date, start_date))
            availabilities = cursor.fetchall()

            for availability in availabilities:
                if start_date <= availability['StartDate'] and end_date >= availability['EndDate']:
                    # The booking completely covers the availability period, so delete it
                    cursor.execute('DELETE FROM Availability WHERE AvailabilityID = ?', (availability['AvailabilityID'],))
                elif start_date > availability['StartDate'] and end_date < availability['EndDate']:
                    # The booking splits the availability period into two, so update the current one and insert a new one
                    cursor.execute('''
                        UPDATE Availability SET EndDate = ?
                        WHERE AvailabilityID = ?
                    ''', (self.subtract_one_day(start_date), availability['AvailabilityID']))
                    cursor.execute('''
                        INSERT INTO Availability (ListingID, StartDate, EndDate)
                        VALUES (?, ?, ?)
                    ''', (listing_id, self.add_one_day(end_date), availability['EndDate']))
                elif start_date > availability['StartDate'] and start_date <= availability['EndDate']:
                    # The booking overlaps the end of the availability period, so update the end date
                    cursor.execute('''
                        UPDATE Availability SET EndDate = ?
                        WHERE AvailabilityID = ?
                    ''', (self.subtract_one_day(start_date), availability['AvailabilityID']))
                elif end_date >= availability['StartDate'] and end_date < availability['EndDate']:
                    # The booking overlaps the start of the availability period, so update the start date
                    cursor.execute('''
                        UPDATE Availability SET StartDate = ?
                        WHERE AvailabilityID = ?
                    ''', (self.add_one_day(end_date), availability['AvailabilityID']))

            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"An error occurred while updating availability: {e}")
            
    def add_one_day(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        new_date = date + timedelta(days=1)
        return new_date.strftime("%Y-%m-%d")

    def subtract_one_day(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        new_date = date - timedelta(days=1)
        return new_date.strftime("%Y-%m-%d")

            
    def is_car_available(self, conn, listing_id, start_date, end_date):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Availability
            WHERE ListingID = ?
            AND StartDate <= ? AND EndDate >= ?
        ''', (listing_id, start_date, end_date))
        available = cursor.fetchall()
        return len(available) > 0  # If there are no conflicting records, it's available


    def create_booking(self, booking_details):
        # Start a transaction
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if not self.is_car_available(
                conn,
                booking_details['listing_id'],
                booking_details['start_date'],
                booking_details['end_date']
            ):
                print("Car is not available for the given date range")
                return None
            # Create the booking
            cursor.execute('''
                INSERT INTO BookingRequests (ListingID, RequesterID, StartDate, EndDate, Status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                booking_details['listing_id'],
                booking_details['renter_id'],
                booking_details['start_date'],
                booking_details['end_date'],
                'Pending'
            ))
            booking_request_id = cursor.lastrowid
            
            conn.commit()
            self.notify(f"Booking Request {booking_request_id} created", booking_request_id, None)  # Notify observers
            conn.close()
            return booking_request_id
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"An error occurred: {e}")
            return None
        
    def approve_booking(self, booking_request_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Retrieve the booking request details
            cursor.execute('''
                SELECT ListingID, StartDate, EndDate FROM BookingRequests WHERE RequestID = ?
            ''', (booking_request_id,))
            booking_request = cursor.fetchone()

            if booking_request:
                # Update the booking request status to 'Confirmed'
                cursor.execute('''
                    UPDATE BookingRequests SET Status = 'Confirmed' WHERE RequestID = ?
                ''', (booking_request_id,))

                # Update car availability
                self.update_car_availability(
                    conn,
                    booking_request['ListingID'],
                    booking_request['StartDate'],
                    booking_request['EndDate']
                )
                
                # Need to calculate booking amount and create a payment record here
                # Get amount from the listing table
                cursor.execute('''
                    SELECT RentalPricing FROM CarListing WHERE ListingID = ?
                ''', (booking_request['ListingID'],))
                amount = cursor.fetchone()['RentalPricing']
                
                cursor.execute('''
                    INSERT INTO Payments (BookingID, UserID, Amount, Status, PaymentMethod)
                    VALUES (?, ?, ?, ?, ?)
                ''', (booking_request_id, booking_request['RequesterID'], amount, 'Pending', 'Wallet'))

                conn.commit()
                self.notify(f"Booking Request {booking_request_id} confirmed", booking_request_id, None)  # Notify observers
                success = True
            else:
                success = False

            conn.close()
            return success
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"An error occurred: {e}")
            conn.close()
            return False


            
    def reject_booking(self, booking_request_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Retrieve the booking request details
            cursor.execute('''
                SELECT RequesterID, ListingID FROM BookingRequests WHERE RequestID = ?
            ''', (booking_request_id,))
            booking_request = cursor.fetchone()
            
            # Delete the booking request
            cursor.execute('''
                DELETE FROM BookingRequests WHERE RequestID = ?
            ''', (booking_request_id,))

            affected_rows = cursor.rowcount
            conn.commit()

            if affected_rows > 0:
                self.notify(f"Booking Request {booking_request_id} rejected and deleted", booking_request_id, booking_request)  # Notify observers
                success = True
            else:
                success = False  # No record was found/deleted

            conn.close()
            return success
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"An error occurred: {e}")
            conn.close()
            return False


            
    def cancel_booking(self, booking_request_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve the booking request details
        cursor.execute('''
            SELECT ListingID, StartDate, EndDate FROM BookingRequests WHERE RequestID = ?
        ''', (booking_request_id,))
        booking_request = cursor.fetchone()

        # Delete the booking request
        cursor.execute('''
            DELETE FROM BookingRequests WHERE RequestID = ?
        ''', (booking_request_id,))

        affected_rows = cursor.rowcount
        conn.commit()

        if affected_rows > 0:
            self.notify(f"Booking request {booking_request_id} canceled and deleted", booking_request_id, booking_request)  # Notify observers
            success = True
        else:
            success = False  # No record was found/deleted

        conn.close()
        return success



        



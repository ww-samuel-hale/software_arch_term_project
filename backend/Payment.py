from Db import get_db_connection

class PaymentService:
    def process_payment(self, amount, booking_id, user_id):
        """
        Process the payment for a booking.
        :param amount: The amount to be paid.
        :param booking_id: The ID of the booking for which payment is being made.
        :param user_id: The ID of the user making the payment.
        :return: A string indicating the result of the payment operation.
        """
        raise NotImplementedError("This method should be overridden in derived classes")


# The actual payment processing service
class RealPaymentService(PaymentService):
    def process_payment(self, amount, booking_id, user_id):
        """
        Perform the actual payment processing logic.
        Here you would integrate with a real payment gateway.
        """
        # Grab Payment Amount from Payments Table Using booking_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Payments WHERE BookingID = ?", (booking_id,))
        
        # Check if the payment has already been processed
        payment = cursor.fetchone()
        if payment["Status"] == "Processed":
            return f"Payment for booking {booking_id} has already been processed."
        
        # Process the payment | Take money out of user's wallet | Put money in owner's wallet
        cursor.execute("UPDATE Users SET WalletBalance = WalletBalance - ? WHERE UserID = ?", (amount, user_id))
        
        # Get the ListingID from the BookingRequests Table
        cursor.execute("SELECT ListingID FROM Bookings WHERE BookingID = ?", (booking_id,))
        listing_id = cursor.fetchone()["ListingID"]
        
        # Get the OwnerID from the CarListing Table
        cursor.execute("SELECT OwnerID FROM CarListing WHERE ListingID = ?", (listing_id,))
        owner_id = cursor.fetchone()["OwnerID"]
        
        # Put money in owner's wallet
        cursor.execute("UPDATE Users SET WalletBalance = WalletBalance + ? WHERE UserID = ?", (amount, owner_id))
        
        # Update the payment status to 'Processed'
        cursor.execute("UPDATE Payments SET Status = 'Processed' WHERE BookingID = ?", (booking_id,))
        
        # Update the Payment method to 'Wallet'
        cursor.execute("UPDATE Payments SET PaymentMethod = 'Wallet' WHERE BookingID = ?", (booking_id,))
        
        # Update the Payment TransactionDate to current time stamp
        cursor.execute("UPDATE Payments SET TransactionDate = CURRENT_TIMESTAMP WHERE BookingID = ?", (booking_id,))
        
        conn.commit()
        conn.close()

        return f"Payment of {amount} for booking {booking_id} by user {user_id} processed successfully."


# Proxy class that adds a layer of security and other pre- or post-processing logic
class PaymentProxy(PaymentService):
    def __init__(self):
        self._real_payment_service = RealPaymentService()

    def process_payment(self, amount, booking_id, user_id):
        # Perform security checks and logging here
        if not self._security_check(user_id):
            return "Security check failed. Payment cannot be processed."

        # Logging the payment attempt
        self._log_payment_attempt(user_id, amount, booking_id)

        # Delegating the actual payment processing to the real payment service
        result = self._real_payment_service.process_payment(amount, booking_id, user_id)

        return result

    def _security_check(self, user_id):
        # Make sure the user exists in the system and has the necessary permissions
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user is None:
            return False
        else: 
            return True

    def _log_payment_attempt(self, user_id, amount, booking_id):
        print(f"User {user_id} attempts to pay {amount} for booking {booking_id}")

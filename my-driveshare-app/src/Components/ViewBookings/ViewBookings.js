import React, { useState, useEffect, useContext } from 'react';
import { get, post } from '../../Utilities/api-utility';
import MyContext from '../../Context/Context';

function ViewBookings({ userId }) {
    const { user } = useContext(MyContext);
    const [bookings, setBookings] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchBookings = async () => {
            try {
                setIsLoading(true);
                // Fetch bookings from your backend; include user authentication as needed
                const response = await get('fetch-bookings');
                setBookings(response.data);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        if (user) {
            fetchBookings();
        }
    }, []);

    if (isLoading) return <div>Loading bookings...</div>;
    if (error) return <div>Error: {error}</div>;

    const handleAcceptBooking = async (requestId) => {
        // Implement the logic to accept the booking
        try {
            let data = {
                booking_id: requestId,
                response: 'accept',
            }
            const response = await post('respond-to-booking', data);
            console.log(response)
        } catch (error) {
            console.error('Error responding to booking:', error);
        }
    }

    const handleRejectBooking = async (requestId) => {
        // Implement the logic to reject the booking
        try {
            let data = {
                booking_id: requestId,
                response: 'reject',
            }
            const response = await post('respond-to-booking', data);
            console.log(response)
        } catch (error) {
            console.error('Error responding to booking:', error);
        }
    }

    const handleCancelBooking = async (requestId) => {
        // Implement the logic to cancel the booking
        try {
            const response = await post(`cancel-booking/${requestId}`);
            console.log(response);
        } catch (error) {
            console.error('Error canceling booking:', error);
        }
    }
    
    return (
        <div>
            {bookings.length === 0 ? (
                <div>No bookings found.</div>
            ) : (
                <ul>
                    {bookings.map((booking) => (
                        <li key={booking.RequestID}>
                            <div>Booking ID: {booking.RequestID}</div>
                            <div>Status: {booking.Status}</div>
                            <div>StartDate: {booking.StartDate}</div>
                            <div>EndDate: {booking.EndDate}</div>
                            {booking.Status === 'pending' && booking.Role === 'requestee' && (
                                <div>
                                    <button onClick={handleAcceptBooking}>Accept</button>
                                    <button onClick={handleRejectBooking}>Reject</button>
                                </div>
                            )}
                            {booking.Status === 'confirmed' && (
                                <div>
                                    <button onClick={handleCancelBooking}>Cancel</button>
                                </div>
                            )}
                            {booking.Status === 'confirmed' && booking.Role === 'requester' && (
                                <div>
                                    Please pay if you have not done so!
                                </div>
                            )}
                            {/* Add more booking details you want to display */}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default ViewBookings;

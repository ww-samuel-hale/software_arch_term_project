import React, { useState, useContext } from 'react';
import '../../../node_modules/bootstrap/dist/css/bootstrap.css';
import '../../../node_modules/bootstrap-icons/font/bootstrap-icons.css';
import { post } from '../../Utilities/api-utility';
import MyContext from '../../Context/Context';

const Home = () => {
    const { user } = useContext(MyContext);
    const [searchParams, setSearchParams] = useState({
        city: '',
        startDate: '',
        endDate: '',
    });
    const [cars, setCars] = useState([]);
    const [activeBooking, setActiveBooking] = useState(null);
    const [bookingDates, setBookingDates] = useState({
        startDate: '',
        endDate: '',
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setSearchParams(prevParams => ({
            ...prevParams,
            [name]: value
        }));
    };

    const handleBookingDatesChange = (e) => {
        const { name, value } = e.target;
        setBookingDates(prevDates => ({
            ...prevDates,
            [name]: value
        }));
    };


    const handleSubmit = async (e) => {
        e.preventDefault();

        // Transforming the state to match the expected API format
        const apiData = {
            pickup_location: searchParams.city,
            from_date: searchParams.startDate,
            to_date: searchParams.endDate,
        };

        try {
            // Sending a POST request to the "search-available-cars" endpoint
            const response = await post('search-available-cars', apiData);
            console.log('Response:', response);
            // Store the cars in state
            setCars(response);
        } catch (error) {
            console.error('Error during API call:', error);
            // Handle any errors here
        }
    };

    const handleStartConversation = async (ownerId) => {
        try {
            const response = await post('start-conversation', { owner_id: ownerId });
            console.log('Conversation started:', response);
            // You can add more code here to handle the response, like showing a notification
        } catch (error) {
            console.error('Error starting conversation:', error);
        }
    };

    const handleBookCar = async (carId) => {
        try {
            const data = {
                listing_id: carId,
                start_date: bookingDates.startDate,
                end_date: bookingDates.endDate,
            };
            const response = await post('create-booking', data);
            console.log('Booking confirmed:', response);
            // Reset the active booking
            setActiveBooking(null);
        } catch (error) {
            console.error('Error booking car:', error);
        }
    };

    return (
        <div className='container mt-3'>
            <h1 className="text-center mb-4">Welcome to the Home Page!</h1>
            {user && (
                <div className="d-flex justify-content-center">
                    <form className="d-flex" onSubmit={handleSubmit} style={{ width: '800px'}}>
                        <div className="input-group">
                            <input 
                                type="text" 
                                name="city" 
                                className="form-control me-2" 
                                placeholder="City" 
                                value={searchParams.city} 
                                onChange={handleInputChange}
                            />
                            <span className="input-group-text">From</span>
                            <input 
                                type="date" 
                                name="startDate" 
                                className="form-control me-2" 
                                value={searchParams.startDate} 
                                onChange={handleInputChange}
                            />
                            <span className="input-group-text">To</span>
                            <input 
                                type="date" 
                                name="endDate" 
                                className="form-control me-2" 
                                value={searchParams.endDate} 
                                onChange={handleInputChange}
                            />
                            <button type="submit" className="btn btn-primary">
                                <i className="bi bi-search"></i>
                            </button>
                        </div>
                    </form>
                </div>
            )}
            {cars.length > 0 && (
                <div className="row mt-4">
                    {cars.map((car) => (
                        <div key={car.ListingID} className="car-card">
                            <h3>{car.Year} {car.Model}</h3>
                            <p>Class: {car.Class ? car.Class : 'Not specified'}</p>
                            <p>Mileage: {car.Mileage.toLocaleString()} miles</p>
                            <p>Pick up: {car.PickUpLocation}</p>
                            <p>Price Per Day: ${car.RentalPricing.toFixed(2)}</p>
                            {car.availability.map((avail, index) => (
                                <p key={index}>Available from {avail.start_date} to {avail.end_date}</p>
                            ))}
                            <button className="btn btn-primary" onClick={() => handleStartConversation(car.OwnerID)}>Message</button>
                            <button className="btn btn-success" onClick={() => setActiveBooking(car.ListingID)}>Book</button>
                            {activeBooking === car.ListingID && (
                                <div>
                                    <input 
                                        type="date" 
                                        name="startDate" 
                                        className="form-control me-2" 
                                        value={bookingDates.startDate} 
                                        onChange={handleBookingDatesChange}
                                    />
                                    <input 
                                        type="date" 
                                        name="endDate" 
                                        className="form-control me-2" 
                                        value={bookingDates.endDate} 
                                        onChange={handleBookingDatesChange}
                                    />
                                    <button className="btn btn-primary" onClick={() => handleBookCar(car.ListingID)}>Confirm Booking</button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Home;

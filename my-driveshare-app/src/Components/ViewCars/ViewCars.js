import React, { useEffect, useState } from 'react';
import './ViewCars.css'; // Ensure to update this CSS file for card styling
import { get } from '../../Utilities/api-utility';

const ViewCars = () => {
    const [cars, setCars] = useState([]);

    async function getCars() {
        try {
            const response = await get('my-cars');
            if (response.status === 200) {
                setCars(response.data);
            } else {
                console.error('Failed to fetch cars');
            }
        } catch (error) {
            console.error('Failed to fetch cars:', error);
        }
    }

    useEffect(() => {
        getCars();
    }, []);

    return (
        <div className="car-container">
            <h1>View Cars</h1>
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
                </div>
            ))}
        </div>
    );
};

export default ViewCars;

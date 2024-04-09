import './CarList.css';
import React, { useState } from 'react';
import { post } from '../../Utilities/api-utility';

function ListCar() {
    const [car, setCar] = useState({
        model: '',
        year: '',
        mileage: '',
        pickup_location: '',
        rental_pricing: '',
        availability: [],
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        const isNumberField = ['year', 'mileage', 'rental_pricing'].includes(name);
        setCar({ ...car, [name]: isNumberField ? Number(value) : value });
    };

    const handleAddAvailability = () => {
        setCar({
            ...car,
            availability: [...car.availability, { start_date: '', end_date: '' }],
        });
    };

    const handleAvailabilityChange = (index, field, value) => {
        const updatedAvailability = car.availability.map((item, i) =>
            i === index ? { ...item, [field]: value } : item
        );
        setCar({ ...car, availability: updatedAvailability });
    };

    const handleRemoveAvailability = (index) => {
        const updatedAvailability = car.availability.filter((_, i) => i !== index);
        setCar({ ...car, availability: updatedAvailability });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = await post('create-listing', car);
            console.log(data);
        } catch (error) {
            console.error(error.message);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                name="model"
                value={car.model}
                onChange={handleInputChange}
                placeholder="Model"
            />
            <input
                type="number"
                name="year"
                value={car.year}
                onChange={handleInputChange}
                placeholder="Year"
            />
            <input
                type="number"
                name="mileage"
                value={car.mileage}
                onChange={handleInputChange}
                placeholder="Mileage"
            />
            <input
                type="text"
                name="pickup_location"
                value={car.pickup_location}
                onChange={handleInputChange}
                placeholder="Pickup Location"
            />
            <input
                type="number"
                name="rental_pricing"
                value={car.rental_pricing}
                onChange={handleInputChange}
                placeholder="Rental Pricing"
            />
            <div>
                {car.availability.map((range, index) => (
                    <div key={index}>
                        <input
                            type="date"
                            value={range.start_date}
                            onChange={(e) => handleAvailabilityChange(index, 'start_date', e.target.value)}
                        />
                        <input
                            type="date"
                            value={range.end_date}
                            onChange={(e) => handleAvailabilityChange(index, 'end_date', e.target.value)}
                        />
                        <button type="button" onClick={() => handleRemoveAvailability(index)}>
                            Remove
                        </button>
                    </div>
                ))}
                <button type="button" onClick={handleAddAvailability}>
                    Add Availability
                </button>
            </div>
            <button type="submit">Submit</button>
        </form>
    );
}

export default ListCar;

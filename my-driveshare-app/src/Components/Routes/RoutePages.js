import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from '../Home/Home';
import Register from '../Register/Register';
import CarList from '../CarList/CarList';
import ViewCars from '../ViewCars/ViewCars';
import ViewBookings from '../ViewBookings/ViewBookings';

function RoutePages() {
    return (
        <div className="router-content">
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/register" element={<Register />} />
                <Route path="/car-list" element={<CarList />} />
                <Route path="/view-cars" element={<ViewCars />} />
                <Route path="/view-bookings" element={<ViewBookings />} />
            </Routes>
        </div>
    );
};

export default RoutePages;

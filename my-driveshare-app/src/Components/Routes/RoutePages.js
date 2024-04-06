import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from '../Home/Home';
import Register from '../Register/Register';

function RoutePages() {
    return (
        <div className="router-content">
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/register" element={<Register />} />
            </Routes>
        </div>
    );
};

export default RoutePages;

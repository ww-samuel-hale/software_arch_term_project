import React, { useContext, useState } from 'react';
import './NavBar.css';
import { post } from '../../Utilities/api-utility';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import MyContext from '../../Context/Context';

const NavBar = () => {
    const { user, login, logout } = useContext(MyContext);
    const [showLoginForm, setShowLoginForm] = useState(false);
    const [showRegisterForm, setShowRegisterForm] = useState(false);
    const [loginError, setLoginError] = useState('');
    const [registerError, setRegisterError] = useState('');
    const navigate = useNavigate();

    function handleLogout() {
        logout();
        navigate('/');
    };

    const handleLoginClick = () => {
        if (user) {
            handleLogout();
        } else {
            setShowLoginForm(!showLoginForm);
            setShowRegisterForm(false);
            setLoginError(''); // Clear previous error messages
        }
    };

    const handleRegister = () => {
        // I just want it to navigate the user to /register
        navigate('/register');
    };

    const submitLogin = async (event) => {
        event.preventDefault();
        const email = event.target.email.value;
        const password = event.target.password.value;
        try {
            let data = {
                "email": email,
                "password": password
            }
            const response = await post('/login', data);
            login();
            setShowLoginForm(false);
            setLoginError('');
        } catch (error) {
            // Assuming the API returns a structured error, you can display a message
            // Adjust based on your API's error structure
            setLoginError(error.response?.data?.message || 'Login failed. Please try again.');
        }
    };

    return (
        <nav className="navbar">
            <Link to ="/" className="navbar-logo">
                <div>DriveShare</div>
            </Link>
            <div className="navbar-menu">
                <button onClick={handleLoginClick}>{user ? 'Logout' : 'Log In'}</button>
                {!user && <button onClick={handleRegister}>Sign up</button>}
            </div>
            {showLoginForm && (
                <div className="login-form-container">
                    <form className="login-form" onSubmit={submitLogin}>
                        <input type="text" placeholder="Email" name="email" required />
                        <input type="password" placeholder="Password" name="password" required />
                        <button type="submit">Login</button>
                        {loginError && <div className="error-message">{loginError}</div>}
                    </form>
                </div>
            )}
        </nav>
    );
};

export default NavBar;

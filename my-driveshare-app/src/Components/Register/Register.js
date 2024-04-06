import React, { useState } from 'react';
import './Register.css';
import { post } from '../../Utilities/api-utility';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [securityQuestions, setSecurityQuestions] = useState({
        question1: '',
        question2: '',
        question3: '',
    });
    const [securityQuestionPrompts] = useState([
        "What is your mother's maiden name?",
        "What was the name of your first pet?",
        "What street did you grow up on?",
    ]);
    const [feedbackMessage, setFeedbackMessage] = useState('');

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        if (name === 'email') {
            setEmail(value);
        } else if (name === 'password') {
            setPassword(value);
        } else {
            setSecurityQuestions((prevQuestions) => ({
                ...prevQuestions,
                [name]: value,
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        // Check if any of the fields are empty
        if (!email || !password || !securityQuestions.question1 || !securityQuestions.question2 || !securityQuestions.question3) {
            setFeedbackMessage('Please fill in all fields before submitting.');
            return; // Stop the function from proceeding further
        }
    
        var securityQuestionsObject = [];
        for (let i = 0; i < securityQuestionPrompts.length; i++) {
            securityQuestionsObject.push({ question: securityQuestionPrompts[i], answer: e.target[i+2].value });
        }
    
        let data = {
            "email": email,
            "password": password,
            "security_questions": securityQuestionsObject
        };
    
        try {
            await post('/register', data);
            setFeedbackMessage('Registration successful!');
        } catch (error) {
            setFeedbackMessage('Registration failed. Please try again.');
        }
    };
    

    return (
        <form onSubmit={handleSubmit}>
            <label>
                Email:
                <input
                    type="email"
                    name="email"
                    value={email}
                    onChange={handleInputChange}
                />
            </label>
            <br />
            <label>
                Password:
                <input
                    type="password"
                    name="password"
                    value={password}
                    onChange={handleInputChange}
                />
            </label>
            <br />
            <label>
                What is your mother's maiden name?
                <input
                    type="text"
                    name="question1"
                    value={securityQuestions.question1}
                    onChange={handleInputChange}
                />
            </label>
            <br />
            <label>
                What was the name of your first pet?
                <input
                    type="text"
                    name="question2"
                    value={securityQuestions.question2}
                    onChange={handleInputChange}
                />
            </label>
            <br />
            <label>
                What street did you grow up on?
                <input
                    type="text"
                    name="question3"
                    value={securityQuestions.question3}
                    onChange={handleInputChange}
                />
            </label>
            <br />
            <button type="submit">Register</button>
            {feedbackMessage && <div>{feedbackMessage}</div>}
        </form>
    );
};

export default Register;
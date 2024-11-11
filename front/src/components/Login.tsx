// src/components/Login.tsx
import React, { useState } from 'react';
import { authenticateUser } from '../services/authService';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/Login.css';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const { access } = await authenticateUser(email, password);
            localStorage.setItem('token', access);
            setMessage('Login successful!');
            navigate('/chat');
        } catch (error) {
            console.error(error);
            setMessage('Failed to login. Check console for details.');
        }
    };

    return (
        <div className="login-container">
            <div className="login-content">
                <div className="login-card">
                    <h2 className="text-center mb-4">Welcome Back!</h2>
                    <form onSubmit={handleLogin}>
                        <div className="form-group mb-3 text-start">
                            <label htmlFor="email">Email</label>
                            <input
                                type="email"
                                id="email"
                                className="form-control"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group mb-3 text-start">
                            <label htmlFor="password">Password</label>
                            <input
                                type="password"
                                id="password"
                                className="form-control"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <button type="submit" className="btn btn-primary w-100">
                            Login
                        </button>
                    </form>
                    {message && <p className="mt-3 text-center text-danger">{message}</p>}
                </div>
            </div>
            <footer className="login-footer">
                <p>&copy; {new Date().getFullYear()} Forum. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default Login;

import Base from '../base/Base';
import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';

function Login() {
    const { setIsAuthenticated } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // TODO
        // if logged properly
        setIsAuthenticated(true);
    };

    return (
        <Base>
        <div className="container">
            <div className="columns is-centered">
                <div className="column is-half">
                    <h1 className="title is-1">Sign in</h1>
                    <form onSubmit={handleSubmit}>
                        <div className="field">
                            <label className="label">Username</label>
                            <div className="control">
                                <input
                                    type="text"
                                    name="username"
                                    className="input"
                                    value={formData.username}
                                    onChange={handleChange}
                                    placeholder="Enter your username"
                                    required
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">Password</label>
                            <div className="control">
                                <input
                                    type="password"
                                    name="password"
                                    className="input"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="Enter your password"
                                    required
                                />
                            </div>
                        </div>
                        <div className="field">
                            <div className="control">
                                <button type="submit" className="button is-link">
                                    Sign in
                                </button>
                            </div>
                        </div>
                    </form>
                    <p>
                        Don't have an account?{' '}
                        <a href="/register">
                            <strong>Register here</strong>
                        </a>!
                    </p>
                </div>
            </div>
        </div>
        </Base>
    );
}

export default Login;

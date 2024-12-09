import Base from '../base/Base';
import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { useNavigate } from 'react-router-dom';

function Register() {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password1: '',
        password2: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('Registration form submitted:', formData);
        await register(formData);
        navigate('/login')
    };

    return (
        <Base>
        <div className="container">
            <div className="columns is-centered">
                <div className="column is-half">
                    <h1 className="title is-1">Create a new account</h1>
                    <form onSubmit={handleSubmit} className="block">
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
                            <label className="label">Email</label>
                            <div className="control">
                                <input
                                    type="email"
                                    name="email"
                                    className="input"
                                    value={formData.email}
                                    onChange={handleChange}
                                    placeholder="Enter your email"
                                    required
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">First name</label>
                            <div className="control">
                                <input
                                    type="text"
                                    name="first_name"
                                    className="input"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    placeholder="Enter your first name"
                                    required
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">Last name</label>
                            <div className="control">
                                <input
                                    type="text"
                                    name="last_name"
                                    className="input"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    placeholder="Enter your last name"
                                    required
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">Password</label>
                            <div className="control">
                                <input
                                    type="password"
                                    name="password1"
                                    className="input"
                                    value={formData.password1}
                                    onChange={handleChange}
                                    placeholder="Enter your password"
                                    required
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">Confirm Password</label>
                            <div className="control">
                                <input
                                    type="password"
                                    name="password2"
                                    className="input"
                                    value={formData.password2}
                                    onChange={handleChange}
                                    placeholder="Confirm your password"
                                    required
                                />
                            </div>
                        </div>
                        <div className="field">
                            <div className="control">
                                <button type="submit" className="button is-link">
                                    Sign Up!
                                </button>
                            </div>
                        </div>
                    </form>
                    <p className="block">
                        If you already have an account,{' '}
                        <a href="/login">
                            <strong>sign in</strong>
                        </a>{' '}
                        instead.
                    </p>
                </div>
            </div>
            </div>
            </Base>
    );
}

export default Register;

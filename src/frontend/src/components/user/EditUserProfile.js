import React, { useState, useEffect } from 'react';
import { useAuth } from '../auth/AuthContext';
import { useNavigate } from 'react-router-dom';

function EditUserProfile() {
    const { is_authenticated, user } = useAuth();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        date_of_birth: '',
        location: '',
    });
    
    useEffect(() => {
        if (!is_authenticated) {
            // Redirect unauthenticated users
            navigate('/login');
        } else {
            // Populate form with user data
            setFormData({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                email: user.email || '',
                date_of_birth: user.date_of_birth || '',
                location: user.location || '',
            });
        }
    }, [user, navigate]);

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
        // Implement form submission logic
        console.log('Submitted data:', formData);
    };

    // Prevent rendering if user is not authenticated
    if (!user || !user.is_authenticated) {
        return null;
    }

    return (
        <div className="container">
            <div className="columns is-centered">
                <div className="column is-half">
                    <h1 className="title is-1">Edit Profile</h1>
                    <form onSubmit={handleSubmit}>
                        <div className="field">
                            <label className="label">First Name</label>
                            <div className="control">
                                <input
                                    type="text"
                                    name="first_name"
                                    className="input"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    placeholder="First Name"
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">Last Name</label>
                            <div className="control">
                                <input
                                    type="text"
                                    name="last_name"
                                    className="input"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    placeholder="Last Name"
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
                                    placeholder="Email"
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">Date of Birth</label>
                            <div className="control">
                                <input
                                    type="date"
                                    name="date_of_birth"
                                    className="input"
                                    value={formData.date_of_birth}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>
                        <div className="field">
                            <label className="label">Location</label>
                            <div className="control">
                                <input
                                    type="text"
                                    name="location"
                                    className="input"
                                    value={formData.location}
                                    onChange={handleChange}
                                    placeholder="Location"
                                />
                            </div>
                        </div>
                        <div className="field">
                            <div className="control">
                                <button type="submit" className="button is-link">
                                    Save Changes
                                </button>
                                <button
                                    type="button"
                                    className="button is-warning"
                                    onClick={() => navigate('/profile')}
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default EditUserProfile;

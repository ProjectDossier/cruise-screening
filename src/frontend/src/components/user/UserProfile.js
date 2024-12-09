import React, { useState, useEffect } from 'react';
import Base from '../base/Base';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    const [userOrganisations, setUserOrganisations] = useState([]);
    const [deleteModalVisible, setDeleteModalVisible] = useState(false);
    const [usernameInput, setUsernameInput] = useState('');

    useEffect(() => {
        // Fetch user data (replace with your API endpoint)
        // TODO
    }, [userId]);

    const handleDeleteAccount = () => {
        if (usernameInput === user?.username) {
            // Call API to delete the user
            // TODO
        }
    };

    if (!user)  return (
        <Base>
            <div className="max-w-3xl mx-auto p-6 bg-white border border-gray-200 rounded-lg shadow-lg my-12 flex justify-center items-center">
                <div className="spinner is-centered animate-spin border-t-4 border-orange-600 border-solid rounded-full w-16 h-16"></div>
            </div>
        </Base>
    );

    return (
        <Base>
            <div className="container">
                <div className="columns is-centered">
                    <div className="column is-half content">
                        <h1 className="is-1">{user.username}</h1>
                        <p><strong>Email:</strong> {user.email}</p>
                        <p><strong>First name:</strong> {user.first_name}</p>
                        <p><strong>Last name:</strong> {user.last_name}</p>
                        <hr />
                        <p><strong>Date of birth:</strong> {user.date_of_birth}</p>
                        <p><strong>Location:</strong> {user.location}</p>
                        <p><strong>Languages:</strong> {user.user_languages}</p>
                        <p><strong>Knowledge areas:</strong> {user.user_knowledge_areas}</p>
                        <p><strong>Allow personalised logging:</strong> {user.allow_logging ? 'Yes' : 'No'}</p>
                        <div>
                            <strong>User organisations:</strong>
                            {userOrganisations.map((org) => (
                                <a
                                    key={org.id}
                                    className="tag m-2"
                                    href={`/view_organisation/${org.id}`}
                                >
                                    {org.title}
                                </a>
                            ))}
                        </div>
                        <hr />
                        <a className="button is-link" href="/edit_user_profile">
                            Edit user
                        </a>
                        <button
                            className="button is-danger"
                            onClick={() => setDeleteModalVisible(true)}
                        >
                            Delete user account
                        </button>
                    </div>
                </div>
            </div>

            {deleteModalVisible && (
                <div className="modal is-active">
                    <div className="modal-background"></div>
                    <div className="modal-card">
                        <header className="modal-card-head">
                            <p className="modal-card-title">
                                Are you sure that you want to delete your user account?
                            </p>
                            <button
                                className="delete"
                                aria-label="close"
                                onClick={() => setDeleteModalVisible(false)}
                            ></button>
                        </header>
                        <section className="modal-card-body">
                            <div className="block">
                                This will delete all your data. This action cannot be undone.
                                To confirm, please type your username: <strong>{user.username}</strong> below.
                            </div>
                            <div className="field">
                                <div className="control">
                                    <input
                                        className="input"
                                        type="text"
                                        placeholder="Username"
                                        value={usernameInput}
                                        onChange={(e) => setUsernameInput(e.target.value)}
                                    />
                                </div>
                            </div>
                        </section>
                        <footer className="modal-card-foot">
                            <button
                                className="button is-danger"
                                disabled={usernameInput !== user.username}
                                onClick={handleDeleteAccount}
                            >
                                Yes, delete my user account
                            </button>
                            <button
                                className="button ml-4"
                                onClick={() => setDeleteModalVisible(false)}
                            >
                                Cancel
                            </button>
                        </footer>
                    </div>
                </div>
            )}
        </Base>
    );
}

export default UserProfile;

import React, { useEffect} from "react";
import { useState } from 'react';

function Header({ user, messages, searchQuery, isSearchResultsPage}) {
    const [isMenuActive] = useState(false);

    useEffect(() => {
        // Get all "navbar-burger" elements
        const navbarBurgers = document.querySelectorAll('.navbar-burger');
        navbarBurgers.forEach((burger) => {
            burger.addEventListener('click', () => {
                // Get the target from the "data-target" attribute
                const target = burger.dataset.target;
                const targetElement = document.getElementById(target);

                // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
                burger.classList.toggle('is-active');
                if (targetElement) targetElement.classList.toggle('is-active');
            });
        });

        return () => {
            navbarBurgers.forEach((burger) => {
                burger.removeEventListener('click', () => {});
            });
        };
    }, []);

    return (
        <>
            <link rel="stylesheet" href="style.css" />
            <nav className="navbar is-light navbar-height" role="navigation" aria-label="main navigation">
                <div className="navbar-brand">
                    <a className="navbar__logo" href="/">
                        <img src="cruise-logo.png" width="60" height="60" alt="Cruise Logo" />
                    </a>

                    <a
                        role="button"
                        className={`navbar-burger ${isMenuActive ? 'is-active' : ''}`}
                        aria-label="menu"
                        aria-expanded="false"
                        data-target="userMenu"
                    >
                        <span aria-hidden="true"></span>
                        <span aria-hidden="true"></span>
                        <span aria-hidden="true"></span>
                    </a>

                    {user?.is_authenticated && (
                        // TODO
                        <a href="">My reviews</a>
                    )}
                    {user?.is_superuser && (
                        // TODO
                        <a href="">
                            Organisations
                        </a>
                    )}
                </div>

                {isSearchResultsPage && (
                    <div className="navbar-menu is-active">
                        <div className="navbar-start">
                            <form id="search_box" className="search-small" method="GET" action="/search">
                                <div className="search-small__input">
                                    <input
                                        type="search"
                                        className="input mr-2"
                                        name="search_query"
                                        defaultValue={searchQuery}
                                        placeholder="Search"
                                        aria-label="Search"
                                    />
                                    <input type="hidden" name="source" value="reformulate_search" />
                                    <button className="button is-primary">Search</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

                <div className="navbar-menu" id="userMenu">
                    <div className="navbar-end">
                        {/* TODO */}
                        <a href="/faq" className="navbar-item">
                            FAQ
                        </a>
                        {user?.is_authenticated ? (
                            <div className="navbar-item has-dropdown is-hoverable">
                                {/* TODO */}
                                <a href="" className="navbar-link">
                                    {user.username}
                                </a>
                                <div className="navbar-dropdown">
                                    {/* TODO */}
                                    <a href="" className="navbar-item">
                                        My profile
                                    </a>
                                    {/* TODO */}
                                    <a href="" className="navbar-item">
                                        My reviews
                                    </a>
                                    <hr className="navbar-divider" />
                                    {/* TODO */}
                                    <a href="" className="navbar-item">
                                        Logout
                                    </a>
                                </div>
                            </div>
                        ) : (
                            <>
                                <a className="js-modal-trigger navbar-item" data-target="modal-sign-up">
                                    <strong>Sign up</strong>
                                </a>
                                {/* TODO */}
                                <a href="" className="navbar-item">
                                    Log in
                                </a>
                            </>
                        )}
                    </div>
                </div>
            </nav>
            {messages?.length > 0 && (
                <div className="messages message">
                    <ul className="messages__list">
                        {messages.map((msg, idx) => (
                            <li key={idx} className={`${msg.tags} message-body`}>
                                {msg.text}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </>
    )
}
export default Header;

import React, { createContext, useState, useContext } from 'react';
import api from '../../api/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(localStorage.getItem('user') != null);
    const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken') || null);
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken') || null);
    const [user, setUser] = useState(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null);

    const login = async (credentials) => {
        try {
            const response = await api.post('/login/', credentials);
            const { access, refresh, user } = response.data;

            setAccessToken(access);
            setRefreshToken(refresh);
            setUser(user);
            localStorage.setItem('accessToken', access);
            localStorage.setItem('refreshToken', refresh);
            localStorage.setItem('user', JSON.stringify(user));

            setIsAuthenticated(true);
            return true;
        } catch (error) {
            alert('Invalid username or password');
            console.error(error);
        }
        return false;
    };

    const register = async (credentials) => {
        try {
            await api.post('/register/', credentials);
            return true;
        } catch (error) {
            alert('Something went wrogn during registartion');
            console.error(error);
        }
        return false;
    };

    const logout = async () => {
        try {
            await api.post('/logout/', {}, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
            });

            setIsAuthenticated(false);
            setAccessToken(null);
            setRefreshToken(null);
            setUser(null);
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');

            return true;
        } catch (error) {
            alert('Something went wrong while logging out');
            console.error(error);
        }
        return false;
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, register, isAuthenticated}}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);

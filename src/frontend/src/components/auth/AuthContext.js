import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false); // Replace with actual auth logic

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
}

export const MockAuthProvider = ({ children, mockUser }) => {
  const value = { user: mockUser, isAuthenticated: !!mockUser };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the mock context
export const useAuth = () => {
  return useContext(AuthContext);
};

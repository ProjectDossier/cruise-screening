import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/home/Home';
import Faq from './components/faq/Faq';
import About from './components/about/About';
import './index.css';
import Login from './components/user/Login';
import Register from './components/user/Register';
import UserProfile from './components/user/UserProfile';
import { AuthProvider } from './components/auth/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import EditUserProfile from './components/user/EditUserProfile';

function App() {
  return (
    <div className="App">
      <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/faq" element={<Faq />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/edit_user_profile" element={<EditUserProfile />} />
          <Route path="/profile"
            element={
                <ProtectedRoute>
                    <UserProfile />
                </ProtectedRoute>
            }/>
        </Routes>
      </Router>
      </AuthProvider>
    </div>
  );
}

export default App;

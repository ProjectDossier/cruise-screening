import React from 'react';
import EditUserProfile from './EditUserProfile';
import { MockAuthProvider } from '../auth/AuthContext';
import { MemoryRouter } from 'react-router-dom';

export default {
  title: 'User/EditUserProfile',
  component: EditUserProfile,
};

const mockUser = {
  is_authenticated: true,
  first_name: 'John',
  last_name: 'Doe',
  email: 'john.doe@example.com',
  date_of_birth: '1980-05-20',
  location: 'Boston',
};

export const Default = () => (
  <MemoryRouter>
    <MockAuthProvider mockUser={mockUser}>
      <EditUserProfile />
    </MockAuthProvider>
  </MemoryRouter>
);

import axios from 'axios';

const API_URL = 'http://localhost:5001/api';

export interface User {
  id: number;
  name: string;
  email: string;
  country?: string;
  state?: string;
  profile_picture?: string;
  is_active: boolean;
  registration_date: string;
  roles: string[];
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

export const authService = {
  async login(credentials: { email: string; password: string }): Promise<AuthResponse> {
    const response = await axios.post(`${API_URL}/auth/login`, credentials);
    if (response.data.access_token) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  },

  async register(data: {
    name: string;
    email: string;
    password: string;
    country?: string;
    state?: string;
  }): Promise<{ message: string; user_id: number }> {
    const response = await axios.post(`${API_URL}/auth/register`, data);
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('user');
  },

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const userData = JSON.parse(userStr);
      return userData.user;
    }
    return null;
  },

  getToken(): string | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const userData = JSON.parse(userStr);
      return userData.access_token;
    }
    return null;
  },
};

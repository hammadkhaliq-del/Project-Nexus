/**
 * Authentication Service
 */
import { api } from './api';
import { ENDPOINTS, STORAGE_KEYS } from '../utils/constants';
import { isTokenExpired } from '../utils/helpers';

class AuthService {
  /**
   * Login user
   */
  async login(username, password) {
    const response = await api.postForm(ENDPOINTS.LOGIN, {
      username,
      password,
    });

    if (response.access_token) {
      localStorage. setItem(STORAGE_KEYS.TOKEN, response.access_token);
      
      // Fetch user info
      const user = await this.getMe();
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
      
      return user;
    }

    throw new Error('Login failed');
  }

  /**
   * Signup new user
   */
  async signup(username, email, password, fullName = null) {
    const response = await api.post(ENDPOINTS.SIGNUP, {
      username,
      email,
      password,
      full_name: fullName,
    });

    if (response.access_token) {
      localStorage.setItem(STORAGE_KEYS.TOKEN, response.access_token);
      
      // Fetch user info
      const user = await this.getMe();
      localStorage.setItem(STORAGE_KEYS.USER, JSON. stringify(user));
      
      return user;
    }

    throw new Error('Signup failed');
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      await api.post(ENDPOINTS.LOGOUT, {});
    } catch (error) {
      // Ignore logout errors
    }

    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
  }

  /**
   * Get current user
   */
  async getMe() {
    return api.get(ENDPOINTS.ME);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    
    if (!token) return false;
    
    return !isTokenExpired(token);
  }

  /**
   * Get stored user
   */
  getUser() {
    const userStr = localStorage.getItem(STORAGE_KEYS.USER);
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Get stored token
   */
  getToken() {
    return localStorage.getItem(STORAGE_KEYS.TOKEN);
  }
}

export const authService = new AuthService();
export default authService;
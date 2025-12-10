/**
 * Auth Store - Simple state management for authentication
 */
import { authService } from '../services/auth';

class AuthStore {
  constructor() {
    this.user = authService.getUser();
    this.isAuthenticated = authService.isAuthenticated();
    this.listeners = new Set();
  }

  /**
   * Subscribe to state changes
   */
  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Notify all listeners
   */
  notify() {
    this.listeners.forEach((listener) => listener(this.getState()));
  }

  /**
   * Get current state
   */
  getState() {
    return {
      user: this.user,
      isAuthenticated: this.isAuthenticated,
    };
  }

  /**
   * Login user
   */
  async login(username, password) {
    try {
      const user = await authService.login(username, password);
      this.user = user;
      this.isAuthenticated = true;
      this.notify();
      return { success: true, user };
    } catch (error) {
      return { success: false, error:  error.message };
    }
  }

  /**
   * Signup user
   */
  async signup(username, email, password, fullName) {
    try {
      const user = await authService.signup(username, email, password, fullName);
      this.user = user;
      this.isAuthenticated = true;
      this.notify();
      return { success: true, user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Logout user
   */
  async logout() {
    await authService.logout();
    this.user = null;
    this.isAuthenticated = false;
    this.notify();
  }

  /**
   * Refresh user data
   */
  async refreshUser() {
    try {
      const user = await authService.getMe();
      this.user = user;
      this.notify();
      return user;
    } catch (error) {
      this.logout();
      return null;
    }
  }

  /**
   * Check authentication status
   */
  checkAuth() {
    this.isAuthenticated = authService. isAuthenticated();
    if (!this.isAuthenticated) {
      this.user = null;
    }
    this.notify();
    return this.isAuthenticated;
  }
}

export const authStore = new AuthStore();
export default authStore;
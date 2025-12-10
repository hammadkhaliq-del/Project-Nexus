/**
 * useAuth Hook - Authentication state management
 */
import { useState, useEffect, useCallback } from 'react';
import { authStore } from '../store/authStore';

export function useAuth() {
  const [state, setState] = useState(authStore.getState());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Subscribe to auth store changes
    const unsubscribe = authStore. subscribe((newState) => {
      setState(newState);
    });

    // Check auth on mount
    authStore.checkAuth();

    return unsubscribe;
  }, []);

  const login = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);

    const result = await authStore.login(username, password);

    setLoading(false);

    if (! result.success) {
      setError(result.error);
    }

    return result;
  }, []);

  const signup = useCallback(async (username, email, password, fullName) => {
    setLoading(true);
    setError(null);

    const result = await authStore. signup(username, email, password, fullName);

    setLoading(false);

    if (!result.success) {
      setError(result.error);
    }

    return result;
  }, []);

  const logout = useCallback(async () => {
    setLoading(true);
    await authStore.logout();
    setLoading(false);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    loading,
    error,
    login,
    signup,
    logout,
    clearError,
  };
}

export default useAuth;
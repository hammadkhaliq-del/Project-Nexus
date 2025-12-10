/**
 * Signup Page
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, User, Mail, Lock, UserPlus, AlertCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

function Signup() {
  const navigate = useNavigate();
  const { signup, isAuthenticated, loading, error, clearError } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    clearError();
    setValidationError('');
  }, [formData, clearError]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidationError('');

    // Validation
    if (formData.password !== formData. confirmPassword) {
      setValidationError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setValidationError('Password must be at least 6 characters');
      return;
    }

    if (formData.username.length < 3) {
      setValidationError('Username must be at least 3 characters');
      return;
    }

    const result = await signup(
      formData.username,
      formData.email,
      formData.password,
      formData.fullName || null
    );

    if (result.success) {
      navigate('/dashboard');
    }
  };

  const displayError = validationError || error;

  return (
    <div className="min-h-screen bg-[#0d1117] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center gap-2 mb-4">
            <Activity className="w-10 h-10 text-[#58a6ff]" />
            <span className="text-3xl font-bold text-white">NEXUS</span>
          </div>
          <p className="text-[#8b949e]">Create your account</p>
        </div>

        {/* Signup Form */}
        <div className="bg-[#161b22] rounded-lg border border-[#30363d] p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Error Display */}
            {displayError && (
              <div className="flex items-center gap-2 p-3 bg-[#f8514922] border border-[#f85149] rounded-md text-[#f85149] text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{displayError}</span>
              </div>
            )}

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-[#c9d1d9] mb-2">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8b949e]" />
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  minLength={3}
                  className="w-full bg-[#0d1117] text-[#c9d1d9] pl-10 pr-4 py-2 rounded-md border border-[#30363d] focus:outline-none focus:border-[#58a6ff] focus:ring-1 focus:ring-[#58a6ff]"
                  placeholder="Choose a username"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-[#c9d1d9] mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8b949e]" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full bg-[#0d1117] text-[#c9d1d9] pl-10 pr-4 py-2 rounded-md border border-[#30363d] focus:outline-none focus: border-[#58a6ff] focus:ring-1 focus:ring-[#58a6ff]"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            {/* Full Name (Optional) */}
            <div>
              <label className="block text-sm font-medium text-[#c9d1d9] mb-2">
                Full Name <span className="text-[#8b949e]">(optional)</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8b949e]" />
                <input
                  type="text"
                  name="fullName"
                  value={formData. fullName}
                  onChange={handleChange}
                  className="w-full bg-[#0d1117] text-[#c9d1d9] pl-10 pr-4 py-2 rounded-md border border-[#30363d] focus:outline-none focus:border-[#58a6ff] focus:ring-1 focus:ring-[#58a6ff]"
                  placeholder="Enter your full name"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-[#c9d1d9] mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8b949e]" />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  minLength={6}
                  className="w-full bg-[#0d1117] text-[#c9d1d9] pl-10 pr-4 py-2 rounded-md border border-[#30363d] focus:outline-none focus: border-[#58a6ff] focus:ring-1 focus:ring-[#58a6ff]"
                  placeholder="Create a password"
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-[#c9d1d9] mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8b949e]" />
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full bg-[#0d1117] text-[#c9d1d9] pl-10 pr-4 py-2 rounded-md border border-[#30363d] focus:outline-none focus:border-[#58a6ff] focus:ring-1 focus: ring-[#58a6ff]"
                  placeholder="Confirm your password"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-[#238636] text-white py-2 px-4 rounded-md font-medium hover:bg-[#2ea043] focus:outline-none focus:ring-2 focus:ring-[#238636] focus:ring-offset-2 focus:ring-offset-[#161b22] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <UserPlus className="w-4 h-4" />
                  Create Account
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-[#8b949e] text-sm">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-[#58a6ff] hover:underline font-medium"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-[#8b949e] text-xs mt-6">
          NEXUS AI-Powered Smart City Simulation
        </p>
      </div>
    </div>
  );
}

export default Signup;
import React, { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import { Activity, Zap, Car, AlertTriangle, Brain, RefreshCw, LogOut } from 'lucide-react';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();
      onLogin(data.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d1117] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#2d7dd2]/10 mb-4">
            <Brain className="w-8 h-8 text-[#2d7dd2]" />
          </div>
          <h1 className="text-3xl font-bold text-[#e6edf3] mb-2">NEXUS AI System</h1>
          <p className="text-[#7d8590]">Smart City Simulation Platform</p>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
          <h2 className="text-xl font-semibold text-[#e6edf3] mb-6">Sign In</h2>
          
          {error && (
            <div className="bg-[#f85149]/10 border border-[#f85149]/20 rounded p-3 mb-4">
              <p className="text-[#f85149] text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-[#e6edf3] text-sm font-medium mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-[#e6edf3] focus:outline-none focus:border-[#2d7dd2]"
              />
            </div>

            <div>
              <label className="block text-[#e6edf3] text-sm font-medium mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-[#e6edf3] focus:outline-none focus:border-[#2d7dd2]"
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full bg-[#2d7dd2] hover:bg-[#2d7dd2]/90 text-white font-medium py-2 px-4 rounded transition-colors disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </div>

          <p className="text-[#7d8590] text-sm text-center mt-4">
            Demo: Use any username/password to create account
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login
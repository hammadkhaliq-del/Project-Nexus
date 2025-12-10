import React, { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import { Activity, Zap, Car, AlertTriangle, Brain, RefreshCw, LogOut } from 'lucide-react';

const Dashboard = ({ onLogout }) => {
  const [cityState, setCityState] = useState(null);
  const [events, setEvents] = useState([]);
  const [reasoning, setReasoning] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [weather, setWeather] = useState('clear');
  const [isRunning, setIsRunning] = useState(false);
  const [layers, setLayers] = useState({
    vehicles: true,
    paths: true,
    grid: true,
    emergencies: true
  });
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect WebSocket
    wsRef.current = new WebSocket('ws://localhost:8000/ws');
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'event') {
        setEvents(prev => [data.data, ...prev].slice(0, 50));
      } else if (data.type === 'reasoning') {
        setReasoning(prev => [data.data, ...prev].slice(0, 50));
      }
    };

    // Fetch initial state
    fetchCityState();
    fetchMetrics();
    
    // Start simulation
    handleStart();

    // Polling for updates
    const interval = setInterval(() => {
      fetchCityState();
      fetchMetrics();
    }, 1000);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchCityState = async () => {
    try {
      const token = localStorage.getItem('nexus_token');
      const response = await fetch('http://localhost:8000/api/state/city', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setCityState(data);
    } catch (err) {
      console.error('Failed to fetch city state:', err);
    }
  };

  const fetchMetrics = async () => {
    try {
      const token = localStorage.getItem('nexus_token');
      const response = await fetch('http://localhost:8000/api/state/metrics', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  };

  const handleStart = async () => {
    try {
      const token = localStorage.getItem('nexus_token');
      await fetch('http://localhost:8000/api/simulation/start', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setIsRunning(true);
    } catch (err) {
      console.error('Failed to start simulation:', err);
    }
  };

  const handlePause = async () => {
    try {
      const token = localStorage.getItem('nexus_token');
      await fetch('http://localhost:8000/api/simulation/pause', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setIsRunning(false);
    } catch (err) {
      console.error('Failed to pause simulation:', err);
    }
  };

  const handleRestart = async () => {
    try {
      const token = localStorage.getItem('nexus_token');
      await fetch('http://localhost:8000/api/simulation/restart', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setEvents([]);
      setReasoning([]);
      setIsRunning(true);
    } catch (err) {
      console.error('Failed to restart simulation:', err);
    }
  };

  const handleWeatherChange = async (newWeather) => {
    try {
      const token = localStorage.getItem('nexus_token');
      await fetch('http://localhost:8000/api/simulation/weather', {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ weather: newWeather })
      });
      setWeather(newWeather);
    } catch (err) {
      console.error('Failed to change weather:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#e6edf3]">
      {/* Header */}
      <header className="bg-[#161b22] border-b border-[#30363d] px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Brain className="text-[#2d7dd2]" />
              NEXUS AI SYSTEM
            </h1>
            <p className="text-[#7d8590] text-sm">Smart City Simulation — 6 AI Engines Active</p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* AI Engine Status Badges */}
            <div className="flex gap-2">
              {['Search', 'CSP', 'Logic', 'HTN', 'Bayesian', 'XAI'].map(engine => (
                <span key={engine} className="px-2 py-1 bg-[#3fb950]/10 text-[#3fb950] text-xs rounded border border-[#3fb950]/20">
                  {engine}
                </span>
              ))}
            </div>
            
            {/* Weather Control */}
            <select 
              value={weather}
              onChange={(e) => handleWeatherChange(e.target.value)}
              className="bg-[#0d1117] border border-[#30363d] rounded px-3 py-1 text-sm text-[#e6edf3] focus:outline-none focus:border-[#2d7dd2]"
            >
              <option value="clear">☀️ Clear</option>
              <option value="rain">🌧️ Rain</option>
              <option value="snow">❄️ Snow</option>
            </select>
            
            {/* Control Buttons */}
            <button
              onClick={isRunning ? handlePause : handleStart}
              className="px-4 py-2 bg-[#2d7dd2] hover:bg-[#2d7dd2]/90 text-white rounded text-sm font-medium transition-colors"
            >
              {isRunning ? 'Pause' : 'Start'}
            </button>
            
            <button
              onClick={handleRestart}
              className="p-2 bg-[#161b22] hover:bg-[#30363d] border border-[#30363d] rounded transition-colors"
              title="Restart Simulation"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            
            <button
              onClick={onLogout}
              className="p-2 bg-[#161b22] hover:bg-[#30363d] border border-[#30363d] rounded transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel - Metrics */}
        <div className="w-80 bg-[#161b22] border-r border-[#30363d] p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold mb-4">System Metrics</h2>
          
          {metrics && (
            <div className="space-y-4">
              <MetricCard 
                icon={<Activity className="w-5 h-5" />}
                label="Efficiency Score"
                value={`${metrics.efficiency_score.toFixed(1)}%`}
                color="text-[#3fb950]"
              />
              <MetricCard 
                icon={<Zap className="w-5 h-5" />}
                label="Power Usage"
                value={`${metrics.power_usage_percent.toFixed(1)}%`}
                color="text-[#d29922]"
              />
              <MetricCard 
                icon={<Car className="w-5 h-5" />}
                label="Active Vehicles"
                value={`${metrics.active_vehicles}/${metrics.total_vehicles}`}
                color="text-[#2d7dd2]"
              />
              <MetricCard 
                icon={<AlertTriangle className="w-5 h-5" />}
                label="Emergencies"
                value={`${metrics.total_emergencies - metrics.resolved_emergencies} Active`}
                color="text-[#f85149]"
              />
            </div>
          )}

          <div className="mt-6">
            <h3 className="text-sm font-semibold mb-3">Layer Toggles</h3>
            <div className="space-y-2">
              {Object.entries(layers).map(([key, value]) => (
                <label key={key} className="flex items-center gap-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={value}
                    onChange={() => setLayers(prev => ({ ...prev, [key]: !prev[key] }))}
                    className="rounded border-[#30363d]"
                  />
                  <span className="text-sm capitalize">{key}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Center - 3D Visualization */}
        <div className="flex-1 bg-[#0d1117] p-4">
          <CityVisualization cityState={cityState} layers={layers} />
        </div>

        {/* Right Panel - Intelligence Feeds */}
        <div className="w-96 bg-[#161b22] border-l border-[#30363d] flex flex-col">
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="p-4 border-b border-[#30363d]">
              <h2 className="text-lg font-semibold">Live Intelligence</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div>
                <h3 className="text-sm font-semibold mb-2 text-[#7d8590]">Events Feed</h3>
                <div className="space-y-2">
                  {events.slice(0, 10).map((event, i) => (
                    <EventCard key={i} event={event} />
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-semibold mb-2 text-[#7d8590]">AI Reasoning</h3>
                <div className="space-y-2">
                  {reasoning.slice(0, 10).map((r, i) => (
                    <ReasoningCard key={i} reasoning={r} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
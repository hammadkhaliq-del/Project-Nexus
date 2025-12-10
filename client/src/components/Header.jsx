/**
 * Header Component - Navigation and controls
 */
import React from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  LogOut, 
  Cloud, 
  CloudRain, 
  CloudSnow,
  Activity
} from 'lucide-react';
import { AI_ENGINES, WEATHER_TYPES } from '../utils/constants';

function Header({ 
  user, 
  isRunning, 
  isPaused, 
  weather, 
  onStart, 
  onPause, 
  onRestart, 
  onWeatherChange, 
  onLogout 
}) {
  const getWeatherIcon = () => {
    switch (weather) {
      case WEATHER_TYPES.RAIN:
        return <CloudRain className="w-4 h-4" />;
      case WEATHER_TYPES. SNOW:
        return <CloudSnow className="w-4 h-4" />;
      default:
        return <Cloud className="w-4 h-4" />;
    }
  };

  return (
    <header className="bg-[#161b22] border-b border-[#30363d] px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Activity className="w-6 h-6 text-[#58a6ff]" />
            <h1 className="text-xl font-bold text-white">NEXUS</h1>
          </div>
          
          {/* AI Engine Badges */}
          <div className="hidden md:flex items-center gap-2">
            {AI_ENGINES.map((engine) => (
              <span
                key={engine. id}
                className="px-2 py-1 text-xs rounded-full bg-[#21262d] text-[#8b949e] border border-[#30363d]"
                title={engine.name}
              >
                {engine.icon} {engine.id. toUpperCase()}
              </span>
            ))}
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          {/* Weather Selector */}
          <div className="relative">
            <select
              value={weather}
              onChange={(e) => onWeatherChange(e.target.value)}
              className="appearance-none bg-[#21262d] text-[#c9d1d9] text-sm px-3 py-2 pr-8 rounded-md border border-[#30363d] focus:outline-none focus: border-[#58a6ff] cursor-pointer"
            >
              <option value={WEATHER_TYPES.CLEAR}>☀️ Clear</option>
              <option value={WEATHER_TYPES.RAIN}>🌧️ Rain</option>
              <option value={WEATHER_TYPES.SNOW}>❄️ Snow</option>
            </select>
            <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-[#8b949e]">
              {getWeatherIcon()}
            </div>
          </div>

          {/* Simulation Controls */}
          <div className="flex items-center gap-2">
            {! isRunning || isPaused ? (
              <button
                onClick={onStart}
                className="flex items-center gap-2 px-3 py-2 bg-[#238636] text-white text-sm font-medium rounded-md hover:bg-[#2ea043] transition-colors"
              >
                <Play className="w-4 h-4" />
                {isPaused ? 'Resume' :  'Start'}
              </button>
            ) : (
              <button
                onClick={onPause}
                className="flex items-center gap-2 px-3 py-2 bg-[#d29922] text-white text-sm font-medium rounded-md hover: bg-[#e3b341] transition-colors"
              >
                <Pause className="w-4 h-4" />
                Pause
              </button>
            )}

            <button
              onClick={onRestart}
              className="flex items-center gap-2 px-3 py-2 bg-[#21262d] text-[#c9d1d9] text-sm font-medium rounded-md border border-[#30363d] hover:bg-[#30363d] transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Restart
            </button>
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-3 pl-3 border-l border-[#30363d]">
            <span className="text-sm text-[#8b949e]">
              {user?. username || 'User'}
            </span>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-3 py-2 text-[#f85149] text-sm font-medium rounded-md hover:bg-[#f8514922] transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
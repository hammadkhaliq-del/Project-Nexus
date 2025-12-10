/**
 * Application Constants
 */

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_BASE_URL  = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';


// API Endpoints
export const ENDPOINTS = {
  // Auth
  LOGIN: '/api/auth/login',
  SIGNUP: '/api/auth/signup',
  ME: '/api/auth/me',
  LOGOUT: '/api/auth/logout',
  
  // Simulation
  SIMULATION_START: '/api/simulation/start',
  SIMULATION_PAUSE: '/api/simulation/pause',
  SIMULATION_RESTART: '/api/simulation/restart',
  SIMULATION_WEATHER:  '/api/simulation/weather',
  SIMULATION_STATUS: '/api/simulation/status',
  
  // State
  STATE_CITY: '/api/state/city',
  STATE_VEHICLES: '/api/state/vehicles',
  STATE_BUILDINGS: '/api/state/buildings',
  STATE_EVENTS: '/api/state/events',
  STATE_REASONING: '/api/state/reasoning',
  STATE_METRICS: '/api/state/metrics',
  
  // WebSocket
  WEBSOCKET:  '/ws'
};

// Weather Types
export const WEATHER_TYPES = {
  CLEAR: 'clear',
  RAIN: 'rain',
  SNOW: 'snow'
};

// Vehicle Types
export const VEHICLE_TYPES = {
  NORMAL: 'normal',
  AMBULANCE: 'ambulance',
  FIRE_TRUCK: 'fire_truck'
};

// Building Types
export const BUILDING_TYPES = {
  RESIDENTIAL: 'residential',
  COMMERCIAL: 'commercial',
  INDUSTRIAL: 'industrial',
  HOSPITAL: 'hospital',
  FIRE_STATION: 'fire_station'
};

// Event Severity
export const SEVERITY = {
  INFO: 'info',
  WARNING: 'warning',
  CRITICAL: 'critical'
};

// AI Engines
export const AI_ENGINES = [
  { id: 'search', name: 'Search (A*)', icon: '🔍', color: '#58a6ff' },
  { id: 'csp', name: 'CSP', icon: '⚡', color: '#f0883e' },
  { id:  'logic', name: 'Logic', icon: '📜', color: '#a371f7' },
  { id: 'htn', name: 'HTN', icon: '🗺️', color: '#3fb950' },
  { id: 'bayesian', name: 'Bayesian', icon: '🎲', color: '#f778ba' },
  { id: 'xai', name: 'XAI', icon: '🧠', color: '#79c0ff' }
];

// Colors
export const COLORS = {
  // Theme
  background: '#0d1117',
  surface: '#161b22',
  border: '#30363d',
  text: '#c9d1d9',
  textSecondary: '#8b949e',
  
  // Status
  success: '#3fb950',
  warning: '#d29922',
  error: '#f85149',
  info: '#58a6ff',
  
  // Buildings
  residential: '#3a4556',
  commercial: '#445566',
  industrial: '#556677',
  hospital: '#d73a4a',
  fireStation: '#f85149',
  
  // Vehicles
  normalVehicle: '#58a6ff',
  ambulance: '#f85149',
  fireTruck: '#f0883e',
  
  // Map
  road: '#21262d',
  park: '#238636',
  blocked: '#f85149'
};

// Simulation
export const SIMULATION = {
  GRID_SIZE: 20,
  DEFAULT_FPS: 12,
  POLL_INTERVAL: 1000
};

// Local Storage Keys
export const STORAGE_KEYS = {
  TOKEN: 'nexus_token',
  USER: 'nexus_user',
  SETTINGS: 'nexus_settings'
};
/**
 * Utility Helper Functions
 */

/**
 * Format a date to readable string
 */
export const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleString();
};

/**
 * Format a timestamp to time only
 */
export const formatTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleTimeString();
};

/**
 * Format number with commas
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString();
};

/**
 * Format percentage
 */
export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%';
  return `${value.toFixed(decimals)}%`;
};

/**
 * Clamp a number between min and max
 */
export const clamp = (num, min, max) => {
  return Math.min(Math.max(num, min), max);
};

/**
 * Generate a unique ID
 */
export const generateId = () => {
  return Math.random().toString(36).substring(2, 9);
};

/**
 * Debounce function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Get severity color
 */
export const getSeverityColor = (severity) => {
  const colors = {
    info: '#58a6ff',
    warning: '#d29922',
    critical: '#f85149'
  };
  return colors[severity] || colors.info;
};

/**
 * Get vehicle color
 */
export const getVehicleColor = (type) => {
  const colors = {
    normal: '#58a6ff',
    ambulance:  '#f85149',
    fire_truck: '#f0883e'
  };
  return colors[type] || colors.normal;
};

/**
 * Get building color
 */
export const getBuildingColor = (type) => {
  const colors = {
    residential: '#3a4556',
    commercial: '#445566',
    industrial: '#556677',
    hospital: '#d73a4a',
    fire_station: '#f85149'
  };
  return colors[type] || colors.residential;
};

/**
 * Calculate distance between two points
 */
export const calculateDistance = (pos1, pos2) => {
  const dx = pos2.x - pos1.x;
  const dy = pos2.y - pos1.y;
  return Math.sqrt(dx * dx + dy * dy);
};

/**
 * Parse JWT token
 */
export const parseJwt = (token) => {
  try {
    const base64Url = token.split('. ')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c. charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
};

/**
 * Check if token is expired
 */
export const isTokenExpired = (token) => {
  const payload = parseJwt(token);
  if (!payload || !payload.exp) return true;
  return Date.now() >= payload.exp * 1000;
};

/**
 * Truncate text
 */
export const truncate = (text, length = 50) => {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
};

/**
 * Capitalize first letter
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Convert snake_case to Title Case
 */
export const snakeToTitle = (str) => {
  if (!str) return '';
  return str
    .split('_')
    .map((word) => capitalize(word))
    .join(' ');
};
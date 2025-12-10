/**
 * Simulation Service
 */
import { api } from './api';
import { ENDPOINTS } from '../utils/constants';

class SimulationService {
  /**
   * Start simulation
   */
  async start() {
    return api.post(ENDPOINTS. SIMULATION_START, {});
  }

  /**
   * Pause simulation
   */
  async pause() {
    return api.post(ENDPOINTS.SIMULATION_PAUSE, {});
  }

  /**
   * Restart simulation
   */
  async restart() {
    return api.post(ENDPOINTS.SIMULATION_RESTART, {});
  }

  /**
   * Change weather
   */
  async setWeather(weather) {
    return api.post(ENDPOINTS.SIMULATION_WEATHER, { weather });
  }

  /**
   * Get simulation status
   */
  async getStatus() {
    return api.get(ENDPOINTS.SIMULATION_STATUS);
  }

  /**
   * Get city state
   */
  async getCityState() {
    return api.get(ENDPOINTS.STATE_CITY);
  }

  /**
   * Get vehicles
   */
  async getVehicles() {
    return api.get(ENDPOINTS.STATE_VEHICLES);
  }

  /**
   * Get buildings
   */
  async getBuildings() {
    return api.get(ENDPOINTS.STATE_BUILDINGS);
  }

  /**
   * Get events
   */
  async getEvents(limit = 50) {
    return api.get(`${ENDPOINTS.STATE_EVENTS}?limit=${limit}`);
  }

  /**
   * Get AI reasoning logs
   */
  async getReasoning(limit = 50) {
    return api.get(`${ENDPOINTS.STATE_REASONING}?limit=${limit}`);
  }

  /**
   * Get simulation metrics
   */
  async getMetrics() {
    return api.get(ENDPOINTS.STATE_METRICS);
  }
}

export const simulationService = new SimulationService();
export default simulationService;
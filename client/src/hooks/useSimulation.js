/**
 * useSimulation Hook - Simulation state management
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { simulationService } from '../services/simulation';
import { SIMULATION } from '../utils/constants';

export function useSimulation() {
  const [state, setState] = useState({
    tick: 0,
    isRunning: false,
    isPaused: false,
    weather: 'clear',
    vehicles: [],
    buildings: [],
    emergencies: [],
    blockedRoads: [],
    gridSize:  SIMULATION.GRID_SIZE,
  });

  const [metrics, setMetrics] = useState({
    efficiencyScore: 100,
    powerUsage: 0,
    activeVehicles: 0,
    activeEmergencies: 0,
    totalEmergencies: 0,
    resolvedEmergencies: 0,
  });

  const [events, setEvents] = useState([]);
  const [reasoning, setReasoning] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const pollIntervalRef = useRef(null);

  // Fetch city state
  const fetchState = useCallback(async () => {
    try {
      const data = await simulationService.getCityState();
      setState({
        tick: data.tick || 0,
        isRunning: data.is_running || false,
        isPaused: data.is_paused || false,
        weather:  data.weather || 'clear',
        vehicles: data.vehicles || [],
        buildings: data.buildings || [],
        emergencies: data.emergencies || [],
        blockedRoads: data.blocked_roads || [],
        gridSize: data.grid_size || SIMULATION.GRID_SIZE,
      });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Fetch metrics
  const fetchMetrics = useCallback(async () => {
    try {
      const data = await simulationService.getMetrics();
      setMetrics({
        efficiencyScore: data.efficiency_score || 100,
        powerUsage: data. power_utilization || 0,
        activeVehicles: data.active_vehicles || 0,
        activeEmergencies: data.active_emergencies || 0,
        totalEmergencies: data.total_emergencies || 0,
        resolvedEmergencies: data.resolved_emergencies || 0,
      });
    } catch (err) {
      console.error('Error fetching metrics:', err);
    }
  }, []);

  // Fetch events
  const fetchEvents = useCallback(async () => {
    try {
      const data = await simulationService. getEvents(50);
      setEvents(data || []);
    } catch (err) {
      console.error('Error fetching events:', err);
    }
  }, []);

  // Fetch reasoning
  const fetchReasoning = useCallback(async () => {
    try {
      const data = await simulationService.getReasoning(50);
      setReasoning(data || []);
    } catch (err) {
      console.error('Error fetching reasoning:', err);
    }
  }, []);

  // Start simulation
  const start = useCallback(async () => {
    try {
      await simulationService.start();
      setState((prev) => ({ ...prev, isRunning: true, isPaused: false }));
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Pause simulation
  const pause = useCallback(async () => {
    try {
      await simulationService.pause();
      setState((prev) => ({ ...prev, isPaused: true }));
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Restart simulation
  const restart = useCallback(async () => {
    try {
      await simulationService.restart();
      await fetchState();
    } catch (err) {
      setError(err.message);
    }
  }, [fetchState]);

  // Set weather
  const setWeather = useCallback(async (weather) => {
    try {
      await simulationService.setWeather(weather);
      setState((prev) => ({ ...prev, weather }));
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Initial fetch and polling
  useEffect(() => {
    const initialize = async () => {
      setLoading(true);
      await Promise.all([fetchState(), fetchMetrics(), fetchEvents(), fetchReasoning()]);
      setLoading(false);
    };

    initialize();

    // Start polling
    pollIntervalRef. current = setInterval(() => {
      fetchState();
      fetchMetrics();
      fetchEvents();
      fetchReasoning();
    }, SIMULATION.POLL_INTERVAL);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef. current);
      }
    };
  }, [fetchState, fetchMetrics, fetchEvents, fetchReasoning]);

  return {
    // State
    ... state,
    metrics,
    events,
    reasoning,
    loading,
    error,

    // Actions
    start,
    pause,
    restart,
    setWeather,
    refresh: fetchState,
  };
}

export default useSimulation;
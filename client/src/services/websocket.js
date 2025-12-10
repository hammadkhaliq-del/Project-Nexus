/**
 * WebSocket Service for Real-time Updates
 */
import { WS_BASE_URL, ENDPOINTS } from '../utils/constants';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;
    this.isConnected = false;
  }

  /**
   * Connect to WebSocket server
   */
  connect(token = null) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    const url = `${WS_BASE_URL}${ENDPOINTS. WEBSOCKET}`;
    
    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this. emit('connected', { connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON. parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console. error('WebSocket message parse error:', error);
        }
      };

      this.ws. onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.emit('disconnected', { code: event.code });
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', { error });
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.attemptReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  /**
   * Attempt to reconnect
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached');
      this.emit('reconnectFailed', {});
      return;
    }

    this.reconnectAttempts++;
    console.log(`Reconnecting...  Attempt ${this.reconnectAttempts}`);

    setTimeout(() => {
      this.connect();
    }, this.reconnectDelay * this.reconnectAttempts);
  }

  /**
   * Handle incoming message
   */
  handleMessage(data) {
    const { type, ... payload } = data;

    // Emit to specific type listeners
    this.emit(type, payload);

    // Emit to 'message' listeners (catch-all)
    this.emit('message', data);
  }

  /**
   * Send message to server
   */
  send(type, data = {}) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return false;
    }

    try {
      this.ws.send(JSON.stringify({ type, data }));
      return true;
    } catch (error) {
      console.error('WebSocket send error:', error);
      return false;
    }
  }

  /**
   * Send ping
   */
  ping() {
    return this.send('ping');
  }

  /**
   * Subscribe to event type
   */
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);

    // Return unsubscribe function
    return () => this.off(eventType, callback);
  }

  /**
   * Unsubscribe from event type
   */
  off(eventType, callback) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).delete(callback);
    }
  }

  /**
   * Emit event to listeners
   */
  emit(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error('WebSocket listener error:', error);
        }
      });
    }
  }

  /**
   * Check if connected
   */
  getConnectionStatus() {
    return this.isConnected;
  }
}

export const wsService = new WebSocketService();
export default wsService;
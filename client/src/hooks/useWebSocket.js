/**
 * useWebSocket Hook - WebSocket connection management
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { wsService } from '../services/websocket';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [events, setEvents] = useState([]);
  const [reasoning, setReasoning] = useState([]);
  const listenersRef = useRef([]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    wsService.connect();
  }, []);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    wsService.disconnect();
  }, []);

  // Send message
  const send = useCallback((type, data) => {
    return wsService.send(type, data);
  }, []);

  // Subscribe to specific message type
  const subscribe = useCallback((messageType, callback) => {
    const unsubscribe = wsService. on(messageType, callback);
    listenersRef.current. push(unsubscribe);
    return unsubscribe;
  }, []);

  useEffect(() => {
    // Handle connection status
    const unsubConnected = wsService.on('connected', () => {
      setIsConnected(true);
    });

    const unsubDisconnected = wsService.on('disconnected', () => {
      setIsConnected(false);
    });

    // Handle incoming messages
    const unsubMessage = wsService.on('message', (data) => {
      setLastMessage(data);

      // Categorize messages
      if (data.type === 'event' || data.category === 'event') {
        setEvents((prev) => [...prev.slice(-99), data]);
      }

      if (data.type === 'reasoning' || data.category === 'ai') {
        setReasoning((prev) => [...prev.slice(-99), data]);
      }
    });

    // Connect on mount
    connect();

    return () => {
      unsubConnected();
      unsubDisconnected();
      unsubMessage();
      
      // Clean up all subscriptions
      listenersRef. current.forEach((unsub) => unsub());
      listenersRef.current = [];
      
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    events,
    reasoning,
    connect,
    disconnect,
    send,
    subscribe,
    clearEvents: () => setEvents([]),
    clearReasoning: () => setReasoning([]),
  };
}

export default useWebSocket;
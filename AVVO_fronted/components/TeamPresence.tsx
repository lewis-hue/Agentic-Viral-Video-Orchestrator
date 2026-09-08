import React, { useState, useEffect } from 'react';
import { User, ChatUser } from '../types';
import { useAuth } from '../contexts/AuthContext';

interface TeamPresenceProps {
    className?: string;
}

const TeamPresence: React.FC<TeamPresenceProps> = ({ className = '' }) => {
    const { user, token } = useAuth();
    const [onlineUsers, setOnlineUsers] = useState<ChatUser[]>([]);
    const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
    const [isConnecting, setIsConnecting] = useState(false);

    useEffect(() => {
        if (!token || !user) return;

        let ws: WebSocket | null = null;
        let reconnectTimeout: NodeJS.Timeout | null = null;
        let reconnectAttempts = 0;
        const maxReconnectAttempts = 5;
        let isComponentMounted = true;

        const connect = () => {
            if (!isComponentMounted || isConnecting) return;

            if (reconnectAttempts >= maxReconnectAttempts) {
                console.error('Max WebSocket reconnection attempts reached');
                setConnectionStatus('disconnected');
                return;
            }

            setIsConnecting(true);
            setConnectionStatus('connecting');

            // Close existing connection if any
            if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
                ws.close();
            }

            const wsUrl = `ws://localhost:8000/api/chat/ws?token=${token}`;
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                if (!isComponentMounted) return;
                console.log('WebSocket connected');
                setConnectionStatus('connected');
                setIsConnecting(false);
                reconnectAttempts = 0; // Reset on successful connection
            };

            ws.onerror = (error) => {
                if (!isComponentMounted) return;
                console.error('WebSocket error:', error);
                setConnectionStatus('disconnected');
                setIsConnecting(false);

                // Log additional error details if available
                if (error.target && (error.target as WebSocket).readyState === WebSocket.CLOSED) {
                    console.error('WebSocket connection failed - connection was closed before establishment');
                }
            };

            ws.onmessage = (event) => {
                if (!isComponentMounted) return;
                try {
                    const data = JSON.parse(event.data);

                    switch (data.type) {
                        case 'online_users':
                            setOnlineUsers(data.online_users || []);
                            break;
                        case 'user_joined':
                            setOnlineUsers(data.online_users || [...data.online_users.filter(u => u.id !== data.user.id), data.user]);
                            break;
                        case 'user_left':
                            setOnlineUsers(data.online_users || []);
                            break;
                        case 'connection_status':
                            setConnectionStatus(data.status);
                            break;
                    }
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            ws.onclose = (event) => {
                if (!isComponentMounted) return;
                console.log('WebSocket closed:', event.code, event.reason);
                setConnectionStatus('disconnected');
                setIsConnecting(false);

                // Attempt to reconnect if not a policy violation (invalid token) and component is still mounted
                if (event.code !== 1008 && reconnectAttempts < maxReconnectAttempts && isComponentMounted && !isConnecting) {
                    reconnectAttempts++;
                    const delay = Math.min(2000 * reconnectAttempts, 30000); // Cap at 30 seconds
                    reconnectTimeout = setTimeout(() => {
                        console.log(`Attempting WebSocket reconnection (${reconnectAttempts}/${maxReconnectAttempts})`);
                        connect();
                    }, delay);
                } else if (event.code === 1008) {
                    console.error('WebSocket connection rejected: Invalid token');
                } else if (reconnectAttempts >= maxReconnectAttempts) {
                    console.error('Max reconnection attempts reached. Giving up.');
                }
            };
        };

        connect();

        return () => {
            isComponentMounted = false;
            if (reconnectTimeout) {
                clearTimeout(reconnectTimeout);
            }
            if (ws) {
                // Only close if connection is established
                if (ws.readyState === WebSocket.OPEN) {
                    ws.close();
                }
            }
        };
    }, [token, user]);

    if (!user) return null;

    return (
        <div className={`flex items-center gap-3 ${className}`}>
            <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-3 py-1 rounded-full border border-white/20">
                <div className={`w-3 h-3 rounded-full ${
                    connectionStatus === 'connected' ? 'bg-green-500' :
                    connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                    'bg-red-500'
                }`} />
                <span className="text-sm font-medium text-white">
                    {onlineUsers.length} online
                </span>
            </div>

            <div className="flex -space-x-2">
                {onlineUsers.slice(0, 5).map((onlineUser, index) => (
                    <div
                        key={`${onlineUser.id}-${index}`}
                        className="w-8 h-8 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center border-2 border-white relative backdrop-blur-sm"
                        title={`${onlineUser.username} (${onlineUser.role})${onlineUser.id === user.id ? ' (You)' : ''}`}
                    >
                        {onlineUser.username.charAt(0).toUpperCase()}
                        {onlineUser.id === user.id && (
                            <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-white rounded-full" />
                        )}
                    </div>
                ))}
                {onlineUsers.length > 5 && (
                    <div className="w-8 h-8 rounded-full bg-gray-300 text-gray-600 text-xs font-bold flex items-center justify-center border-2 border-white backdrop-blur-sm">
                        +{onlineUsers.length - 5}
                    </div>
                )}
            </div>
        </div>
    );
};

export default TeamPresence;
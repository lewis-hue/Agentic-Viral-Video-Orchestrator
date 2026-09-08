import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { Notification, OnlineUser } from '../types';
import { apiService } from '../services/apiService';
import { useAuth } from './AuthContext';

interface NotificationContextType {
    notifications: Notification[];
    unreadCount: number;
    onlineUsers: OnlineUser[];
    addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
    markAsRead: (id: string) => void;
    markAllAsRead: () => void;
    removeNotification: (id: string) => void;
    clearAll: () => void;
    fetchNotifications: () => void;
    fetchOnlineUsers: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (context === undefined) {
        throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
};

interface NotificationProviderProps {
    children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
    const { token } = useAuth();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [onlineUsers, setOnlineUsers] = useState<OnlineUser[]>([]);

    const fetchNotifications = useCallback(async () => {
        if (token) {
            try {
                const data = await apiService.getNotifications(token);
                setNotifications(data.map(n => ({ ...n, timestamp: n.timestamp })));
            } catch (error) {
                console.error('Failed to fetch notifications');
            }
        }
    }, [token]);

    const fetchOnlineUsers = useCallback(async () => {
        if (token) {
            try {
                const data = await apiService.getOnlineUsers(token);
                setOnlineUsers(data);
            } catch (error) {
                console.error('Failed to fetch online users');
            }
        }
    }, [token]);

    useEffect(() => {
        fetchNotifications();
        fetchOnlineUsers();
    }, [fetchNotifications, fetchOnlineUsers]);

    const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
        const newNotification: Notification = {
            ...notification,
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString(),
            read: false,
        };

        setNotifications(prev => [newNotification, ...prev]);

        // Auto-remove notification after 5 seconds for non-error types
        if (notification.type !== 'failed_task') {
            setTimeout(() => {
                setNotifications(prev => prev.filter(n => n.id !== newNotification.id));
            }, 5000);
        }
    }, []);

    const markAsRead = useCallback(async (id: string) => {
        if (token) {
            try {
                await apiService.markNotificationRead(token, id);
                setNotifications(prev =>
                    prev.map(n => n.id === id ? { ...n, read: true } : n)
                );
            } catch (error) {
                console.error('Failed to mark notification as read');
            }
        }
    }, [token]);

    const markAllAsRead = useCallback(async () => {
        if (token) {
            try {
                await apiService.markAllNotificationsRead(token);
                setNotifications(prev =>
                    prev.map(n => ({ ...n, read: true }))
                );
            } catch (error) {
                console.error('Failed to mark all notifications as read');
            }
        }
    }, [token]);

    const removeNotification = useCallback(async (id: string) => {
        if (token) {
            try {
                await apiService.deleteNotification(token, id);
                setNotifications(prev => prev.filter(n => n.id !== id));
            } catch (error) {
                console.error('Failed to delete notification');
            }
        }
    }, [token]);

    const clearAll = useCallback(async () => {
        if (token) {
            try {
                await apiService.clearAllNotifications(token);
                setNotifications([]);
            } catch (error) {
                console.error('Failed to clear all notifications');
            }
        }
    }, [token]);

    const unreadCount = notifications.filter(n => !n.read).length;

    return (
        <NotificationContext.Provider value={{
            notifications,
            unreadCount,
            onlineUsers,
            addNotification,
            markAsRead,
            markAllAsRead,
            removeNotification,
            clearAll,
            fetchNotifications,
            fetchOnlineUsers,
        }}>
            {children}
        </NotificationContext.Provider>
    );
};
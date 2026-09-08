import React, { useState } from 'react';
import { useNotifications } from '../contexts/NotificationContext';
import Button from './Button';

const NotificationCenter: React.FC = () => {
    const { notifications, unreadCount, onlineUsers, markAsRead, markAllAsRead, removeNotification, clearAll } = useNotifications();
    const [isOpen, setIsOpen] = useState(false);

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'new_comment': return '💬';
            case 'new_chat': return '💬';
            case 'failed_task': return '❌';
            case 'successful_task': return '✅';
            case 'version_update': return '🔄';
            case 'document_change': return '📄';
            default: return 'ℹ️';
        }
    };

    const getNotificationColor = (type: string) => {
        switch (type) {
            case 'new_comment': return 'border-l-blue-500 bg-blue-50';
            case 'new_chat': return 'border-l-green-500 bg-green-50';
            case 'failed_task': return 'border-l-red-500 bg-red-50';
            case 'successful_task': return 'border-l-green-500 bg-green-50';
            case 'version_update': return 'border-l-yellow-500 bg-yellow-50';
            case 'document_change': return 'border-l-purple-500 bg-purple-50';
            default: return 'border-l-gray-500 bg-gray-50';
        }
    };

    const getInitials = (username: string) => {
        return username.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2);
    };

    return (
        <div className="relative">
            <Button
                variant="secondary"
                size="sm"
                onClick={() => setIsOpen(!isOpen)}
                className="relative"
            >
                🔔
                {unreadCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {unreadCount > 99 ? '99+' : unreadCount}
                    </span>
                )}
            </Button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-96 max-h-96 frosted-glass-panel z-50">
                    <div className="p-4 border-b border-border">
                        <div className="flex justify-between items-center">
                            <h3 className="font-bold">Notifications</h3>
                            <div className="flex gap-2">
                                {unreadCount > 0 && (
                                    <button
                                        onClick={markAllAsRead}
                                        className="text-xs text-blue-600 hover:text-blue-800"
                                    >
                                        Mark all read
                                    </button>
                                )}
                                <button
                                    onClick={clearAll}
                                    className="text-xs text-gray-600 hover:text-gray-800"
                                >
                                    Clear all
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Online Users Section */}
                    <div className="p-4 border-b border-border bg-gray-50">
                        <div className="text-sm font-medium mb-2 text-gray-700">
                            Online Users ({onlineUsers.length})
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {onlineUsers.map(user => (
                                <div key={user.id} className="flex items-center gap-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs border border-green-300">
                                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                                    {getInitials(user.username)} ({user.role})
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="max-h-80 overflow-y-auto">
                        {notifications.length === 0 ? (
                            <div className="p-4 text-center text-gray-500">
                                No notifications
                            </div>
                        ) : (
                            notifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${getNotificationColor(notification.type)} ${
                                        !notification.read ? 'bg-blue-50' : ''
                                    }`}
                                    onClick={() => markAsRead(notification.id)}
                                >
                                    <div className="flex items-start gap-3">
                                        <span className="text-lg">{getNotificationIcon(notification.type)}</span>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-start">
                                                <h4 className="font-medium text-sm">{notification.title}</h4>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        removeNotification(notification.id);
                                                    }}
                                                    className="text-gray-400 hover:text-gray-600 text-sm"
                                                >
                                                    ×
                                                </button>
                                            </div>
                                            <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                                            <p className="text-xs text-gray-400 mt-2">
                                                {new Date(notification.timestamp).toLocaleTimeString()}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationCenter;
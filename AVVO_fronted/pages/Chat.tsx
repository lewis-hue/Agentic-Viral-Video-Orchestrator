
import React, { useState, useEffect, useRef } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import VoiceToText from '../components/VoiceToText';
import { useAuth } from '../contexts/AuthContext';
import { useNotifications } from '../contexts/NotificationContext';
import { apiService } from '../services/apiService';
import { ChatMessage, Page, User, ChatUser } from '../types';
import { useApp } from '../contexts/AppContext';

interface ChatProps {
    setActivePage: (page: Page) => void;
}

const Chat: React.FC<ChatProps> = ({ setActivePage }) => {
    const { user, token } = useAuth();
    const { addLog } = useApp();
    const { addNotification } = useNotifications();
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [onlineUsers, setOnlineUsers] = useState<ChatUser[]>([]);
    const [isTyping, setIsTyping] = useState<string[]>([]);
    const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // WebSocket message handler
    const handleWebSocketMessage = (event: MessageEvent) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
            case 'message':
                // Add initial or recent messages, avoiding duplicates
                setMessages(prev => {
                    const exists = prev.some(msg => msg.id === data.message.id);
                    if (!exists) {
                        return [...prev, data.message];
                    }
                    return prev;
                });
                break;
            case 'new_message':
                setMessages(prev => [...prev, data.message]);
                // Add notification for new messages from other users
                if (data.message.user_id !== user?.id) {
                    addNotification({
                        type: 'new_chat',
                        title: 'New Chat Message',
                        message: `${data.message.username} (${data.message.role}): ${data.message.message.length > 50 ? data.message.message.substring(0, 50) + '...' : data.message.message}`,
                        actionUrl: '#chat'
                    });
                }
                break;
            case 'online_users':
                setOnlineUsers(data.online_users);
                break;
            case 'user_joined':
                setOnlineUsers(data.online_users);
                if (data.user.id !== user?.id) {
                    addNotification({
                        type: 'new_chat',
                        title: 'User Online',
                        message: `${data.user.username} joined the chat`,
                    });
                }
                break;
            case 'user_left':
                setOnlineUsers(data.online_users);
                break;
            case 'typing_start':
                setIsTyping(prev => [...prev.filter(id => id !== data.user_id), data.user_id]);
                break;
            case 'typing_stop':
                setIsTyping(prev => prev.filter(id => id !== data.user_id));
                break;
            case 'message_deleted':
                setMessages(prev => prev.filter(msg => msg.id !== data.message_id));
                break;
            case 'new_comment':
                // Add notification for new comments
                addNotification({
                    type: 'new_comment',
                    title: 'New Comment',
                    message: `${data.comment.username} (${data.comment.role}): ${data.comment.title}`,
                    actionUrl: '#comments'
                });
                break;
            case 'connection_status':
                setConnectionStatus(data.status);
                break;
        }
    };

    // WebSocket connection setup
    const connectWebSocket = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const wsUrl = `ws://localhost:3000/api/chat/ws?token=${token}`;
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
            console.log('WebSocket connected to chat server');
            setConnectionStatus('connected');
            addLog('INFO', 'Connected to chat server');
        };

        wsRef.current.onmessage = handleWebSocketMessage;

        wsRef.current.onclose = () => {
            console.log('WebSocket disconnected from chat server');
            setConnectionStatus('disconnected');
            addLog('INFO', 'Disconnected from chat server');
            // Attempt to reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
        };

        wsRef.current.onerror = (error) => {
            console.error('WebSocket error occurred', error);
            addLog('ERROR', 'WebSocket error occurred');
            setConnectionStatus('disconnected');
        };
    };

    // Send typing indicator
    const sendTypingIndicator = (isTyping: boolean) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: isTyping ? 'typing_start' : 'typing_stop',
                user_id: user?.id
            }));
        }
    };

    useEffect(() => {
        const fetchMessages = async () => {
            setIsLoading(true);
            try {
                const data = await apiService.getChatMessages(token!);
                setMessages(data.filter(msg => msg.status !== 'deleted'));
                addLog('INFO', 'Fetched chat history.');
            } catch (error) {
                addLog('ERROR', 'Failed to fetch chat history.');
            }
            setIsLoading(false);
        };

        if (token && user) {
            fetchMessages();
            connectWebSocket();
        }

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (typingTimeoutRef.current) {
                clearTimeout(typingTimeoutRef.current);
            }
        };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [token]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newMessage.trim() || !user || !wsRef.current) return;

        const messageText = newMessage.trim();
        setNewMessage('');

        // Stop typing indicator
        sendTypingIndicator(false);
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        }

        // Send message via WebSocket
        if (wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'message',
                message: messageText
            }));
        } else {
            // Fallback to HTTP if WebSocket is not connected
            try {
                const sentMessage = await apiService.sendChatMessage(token!, messageText);
                setMessages(prev => [...prev, sentMessage]);
            } catch (error) {
                addLog('ERROR', 'Failed to send chat message.');
                setNewMessage(messageText); // Restore message on failure
            }
        }
    };

    // Handle typing indicators
    const handleTyping = () => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        sendTypingIndicator(true);

        // Clear existing timeout
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        }

        // Stop typing indicator after 2 seconds of inactivity
        typingTimeoutRef.current = setTimeout(() => {
            sendTypingIndicator(false);
        }, 2000);
    };

    const handleDeleteMessage = (messageId: string) => {
        if (!confirm('Are you sure you want to delete this message?')) return;

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'delete_message',
                message_id: messageId
            }));
            addLog('SUCCESS', `Message ${messageId} deleted.`);
            addNotification({
                type: 'success',
                title: 'Message Deleted',
                message: 'The message has been deleted successfully.',
                actionUrl: '#chat'
            });
        } else {
            addLog('ERROR', 'WebSocket not connected.');
            addNotification({
                type: 'error',
                title: 'Delete Failed',
                message: 'Failed to delete the message. Please try again.',
            });
        }
    };
    
    return (
        <div>
            <BackButton setActivePage={setActivePage} />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Team Chat</h1>

            {/* Connection Status */}
            <div className="mb-6">
                <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
                    connectionStatus === 'connected' ? 'bg-green-100 text-green-800' :
                    connectionStatus === 'connecting' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                }`}>
                    <div className={`w-2 h-2 rounded-full ${
                        connectionStatus === 'connected' ? 'bg-green-500' :
                        connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                        'bg-red-500'
                    }`} />
                    {connectionStatus === 'connected' ? 'Connected' :
                     connectionStatus === 'connecting' ? 'Connecting...' :
                     'Disconnected'}
                </div>
            </div>

            <Card title="Team Chat">
                <div className="flex flex-col h-[75vh]">
                    {/* Online Users */}
                    <div className="mb-6 p-4 frosted-glass-panel rounded-lg border border-white/20">
                        <div className="text-sm font-medium mb-2 text-white">Online Users ({onlineUsers.length})</div>
                        <div className="flex flex-wrap gap-2">
                            {onlineUsers.map(user => (
                                <div key={user.id} className="flex items-center gap-2 bg-green-100/20 backdrop-blur-sm text-green-200 px-2 py-1 rounded-full text-xs border border-green-300/30">
                                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                                    {user.username} ({user.role})
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-grow p-6 frosted-glass-panel rounded-lg overflow-y-auto mb-6 border border-white/20">
                        {isLoading ? <p className="text-white">Loading messages...</p> : (
                            messages.map(msg => (
                                <div key={msg.id} className={`mb-4 ${msg.user_id === user?.id ? 'text-right' : 'text-left'}`}>
                                    <div className={`inline-block p-4 rounded-lg max-w-lg backdrop-blur-sm ${msg.user_id === user?.id ? 'bg-primary/80 text-white border border-primary/50' : 'bg-white/20 text-white border border-white/30'}`}>
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <div className="font-bold text-sm">{msg.username} ({msg.role || 'user'})</div>
                                                <p className="leading-relaxed">{msg.message}</p>
                                                <div className="text-xs opacity-70 mt-2">{new Date(msg.timestamp).toLocaleTimeString()}</div>
                                            </div>
                                            {msg.user_id === user?.id && (
                                                <Button
                                                    size="sm"
                                                    variant="secondary"
                                                    onClick={() => handleDeleteMessage(msg.id)}
                                                >
                                                    Delete
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Typing Indicators */}
                    {isTyping.length > 0 && (
                        <div className="mb-4 text-sm text-gray-500 italic leading-relaxed">
                            {isTyping.length === 1
                                ? `${onlineUsers.find(u => u.id === isTyping[0])?.username || 'Someone'} (${onlineUsers.find(u => u.id === isTyping[0])?.role || 'user'}) is typing...`
                                : `${isTyping.length} people are typing...`
                            }
                        </div>
                    )}

                    {/* Message Input */}
                    <div className="space-y-4">
                        <form onSubmit={handleSendMessage} className="flex gap-4">
                            <div className="relative flex-grow">
                                <input
                                    type="text"
                                    value={newMessage}
                                    onChange={(e) => {
                                        setNewMessage(e.target.value);
                                        handleTyping();
                                    }}
                                    onKeyPress={handleTyping}
                                    placeholder="Type your message..."
                                    className="w-full p-3 pr-10 border border-border rounded-lg"
                                    disabled={connectionStatus !== 'connected'}
                                />
                                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                    <VoiceToText
                                        onTranscription={(text) => {
                                            setNewMessage(prev => prev + text);
                                            handleTyping();
                                        }}
                                    />
                                </div>
                            </div>
                            <Button
                                type="submit"
                                disabled={!newMessage.trim() || connectionStatus !== 'connected'}
                            >
                                Send
                            </Button>
                        </form>
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default Chat;

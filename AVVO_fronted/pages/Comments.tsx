
import React, { useState, useEffect, useRef } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import VoiceToText from '../components/VoiceToText';
import { useAuth } from '../contexts/AuthContext';
import { useNotifications } from '../contexts/NotificationContext';
import { apiService } from '../services/apiService';
import { Comment, User, Page } from '../types';
import { useApp } from '../contexts/AppContext';

const getPriorityColor = (priority: string) => {
    switch (priority) {
        case 'high': return 'text-red-600 font-bold';
        case 'critical': return 'text-red-800 font-extrabold';
        case 'medium': return 'text-yellow-600 font-semibold';
        default: return 'text-gray-600';
    }
};

const getStatusColor = (status: string) => {
    switch (status) {
        case 'open': return 'text-red-600';
        case 'in_progress': return 'text-blue-600';
        case 'resolved': return 'text-green-600';
        case 'closed': return 'text-gray-600';
        case 'deleted': return 'text-gray-400';
        default: return 'text-gray-600';
    }
};


const Comments: React.FC = () => {
    const { user, token } = useAuth();
    const { addLog } = useApp();
    const { addNotification } = useNotifications();
    const [myComments, setMyComments] = useState<Comment[]>([]);
    const [allComments, setAllComments] = useState<Comment[]>([]);
    const [isLoadingMy, setIsLoadingMy] = useState(false);
    const [isLoadingAll, setIsLoadingAll] = useState(false);
    
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [category, setCategory] = useState<'feature' | 'bug' | 'improvement' | 'ui' | 'performance'>('feature');
    const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');
    const [responseText, setResponseText] = useState('');
    const [respondingTo, setRespondingTo] = useState<string | null>(null);
    const [filterStatus, setFilterStatus] = useState<string>('all');
    const [onlineUsers, setOnlineUsers] = useState<any[]>([]);
    const wsRef = useRef<WebSocket | null>(null);

    // WebSocket message handler
    const handleWebSocketMessage = (event: MessageEvent) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
            case 'online_users':
                setOnlineUsers(data.online_users);
                break;
            case 'user_joined':
                setOnlineUsers(data.online_users);
                break;
            case 'user_left':
                setOnlineUsers(data.online_users);
                break;
            case 'new_comment':
                // Refresh comments or add notification
                addNotification({
                    type: 'new_comment',
                    title: 'New Comment',
                    message: `${data.comment.username} (${data.comment.role}): ${data.comment.title}`,
                    actionUrl: '#comments'
                });
                fetchMyComments();
                if (user?.role === 'admin') fetchAllComments();
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
        };

        wsRef.current.onmessage = handleWebSocketMessage;

        wsRef.current.onclose = () => {
            console.log('WebSocket disconnected from chat server');
            // Attempt to reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
        };

        wsRef.current.onerror = (error) => {
            console.error('WebSocket error occurred', error);
        };
    };

    const fetchMyComments = async () => {
        setIsLoadingMy(true);
        try {
            const data = await apiService.getMyComments(token!);
            setMyComments(data);
            addLog('INFO', 'Fetched my comments.');
        } catch (error) {
            addLog('ERROR', 'Failed to fetch my comments.');
        }
        setIsLoadingMy(false);
    };

    const fetchAllComments = async () => {
        if (user?.role !== 'admin') return;
        setIsLoadingAll(true);
        try {
            const data = await apiService.getComments(token!);
            setAllComments(data);
             addLog('INFO', 'Fetched all comments (Admin).');
        } catch (error) {
             addLog('ERROR', 'Failed to fetch all comments.');
        }
        setIsLoadingAll(false);
    };

    const fetchOnlineUsers = async () => {
        try {
            const data = await apiService.getOnlineUsers(token!);
            setOnlineUsers(data);
        } catch (error) {
            addLog('ERROR', 'Failed to fetch online users.');
        }
    };

    useEffect(() => {
        if (token && user) {
            fetchMyComments();
            if (user?.role === 'admin') {
                fetchAllComments();
            }
            fetchOnlineUsers();
            connectWebSocket();
        }

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [token, user]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if(!title.trim() || !description.trim()) {
            alert("Title and description cannot be empty.");
            return;
        }
        try {
            await apiService.submitComment(token!, { title, description, category, priority });
            addLog('SUCCESS', `New comment submitted: ${title}`);
            addNotification({
                type: 'success',
                title: 'Comment Submitted',
                message: `Your comment "${title}" has been submitted successfully.`,
                actionUrl: '#comments'
            });
            setTitle('');
            setDescription('');
            fetchMyComments();
        } catch (error) {
            addLog('ERROR', `Failed to submit comment: ${error}`);
            addNotification({
                type: 'error',
                title: 'Submission Failed',
                message: 'Failed to submit your comment. Please try again.',
            });
        }
    };
    
    const handleUpdateStatus = async (id: string, status: Comment['status']) => {
        try {
            await apiService.updateComment(token!, id, { status });
            addLog('SUCCESS', `Comment #${id} status updated to ${status}.`);
            fetchAllComments();
        } catch(e) {
            addLog('ERROR', `Failed to update comment #${id} status.`);
        }
    }

    const handleAddResponse = async (commentId: string) => {
        if (!responseText.trim() || !commentId || commentId === 'null') return;

        try {
            await apiService.updateComment(token!, commentId, { response: responseText });
            addLog('SUCCESS', `Response added to comment #${commentId}.`);
            addNotification({
                type: 'success',
                title: 'Response Added',
                message: `Your response to comment #${commentId} has been added successfully.`,
                actionUrl: '#comments'
            });
            setResponseText('');
            setRespondingTo(null);
            fetchAllComments();
        } catch(e) {
            addLog('ERROR', `Failed to add response to comment #${commentId}.`);
            addNotification({
                type: 'error',
                title: 'Response Failed',
                message: 'Failed to add response. Please try again.',
            });
        }
    }

    const handleDeleteComment = async (commentId: string) => {
        if (!confirm('Are you sure you want to delete this comment?')) return;

        try {
            await apiService.deleteComment(token!, commentId);
            addLog('SUCCESS', `Comment #${commentId} deleted.`);
            addNotification({
                type: 'success',
                title: 'Comment Deleted',
                message: 'The comment has been deleted successfully.',
                actionUrl: '#comments'
            });
            fetchMyComments();
            if (user?.role === 'admin') fetchAllComments();
        } catch(e) {
            addLog('ERROR', `Failed to delete comment #${commentId}.`);
            addNotification({
                type: 'error',
                title: 'Delete Failed',
                message: 'Failed to delete the comment. Please try again.',
            });
        }
    }

    const startResponse = (commentId: string) => {
        setRespondingTo(commentId);
        setResponseText('');
    }
    
    return (
        <div>
            <BackButton />
            <h1 className="text-3xl font-bold mb-8 leading-relaxed">Comments & Issues</h1>

            {/* Online Users */}
            <div className="mb-6 p-4 frosted-glass-panel rounded-lg border border-white/20">
                <div className="text-sm font-medium mb-2 text-white">Online Users ({onlineUsers.length})</div>
                <div className="flex flex-wrap gap-2">
                    {onlineUsers.map(user => (
                        <div key={user.user_id} className="flex items-center gap-2 bg-green-100/20 backdrop-blur-sm text-green-200 px-2 py-1 rounded-full text-xs border border-green-300/30">
                            <div className="w-2 h-2 bg-green-500 rounded-full" />
                            {user.username} ({user.role})
                        </div>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <div className="space-y-8">
                    <Card title="Submit New Comment">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label htmlFor="commentTitle" className="sr-only">Comment Title</label>
                                <div className="relative">
                                    <input id="commentTitle" value={title} onChange={e => setTitle(e.target.value)} placeholder="Title" className="w-full p-3 pr-10 border border-border rounded-lg" />
                                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                                        <VoiceToText
                                            onTranscription={(text) => setTitle(prev => prev + text)}
                                        />
                                    </div>
                                </div>
                            </div>
                            <label htmlFor="commentDescription" className="sr-only">Comment Description</label>
                            <textarea id="commentDescription" value={description} onChange={e => setDescription(e.target.value)} placeholder="Description" className="w-full p-3 border border-border rounded-lg min-h-[120px]" />
                            <div className="grid grid-cols-2 gap-6">
                               <div>
                                   <label htmlFor="commentCategory" className="sr-only">Category</label>
                                   <select id="commentCategory" value={category} onChange={e => setCategory(e.target.value as any)} className="w-full p-3 border border-border rounded-lg">
                                        <option value="feature">Feature Request</option>
                                        <option value="bug">Bug Report</option>
                                        <option value="improvement">Improvement</option>
                                        <option value="ui">UI/UX</option>
                                        <option value="performance">Performance</option>
                                    </select>
                               </div>
                                <div>
                                    <label htmlFor="commentPriority" className="sr-only">Priority</label>
                                    <select id="commentPriority" value={priority} onChange={e => setPriority(e.target.value as any)} className="w-full p-3 border border-border rounded-lg">
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>
                            </div>
                            <Button type="submit">Submit Comment</Button>
                        </form>
                    </Card>

                    <Card title="My Comments">
                        <Button variant="secondary" onClick={fetchMyComments} isLoading={isLoadingMy} className="mb-6 text-sm py-2 px-3 sm:text-base sm:py-3 sm:px-6">Refresh</Button>
                        <div className="space-y-6 max-h-[32rem] overflow-y-auto pr-2">
                            {myComments.map(c => (
                                <div key={c.id} className="p-6 border border-border rounded-lg frosted-glass-panel">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-bold text-white">{c.title}</h4>
                                            <p className="text-sm text-white/80 leading-relaxed">{c.description}</p>
                                            <div className="text-xs mt-3 flex justify-between">
                                                <span className={getPriorityColor(c.priority)}>{c.priority.toUpperCase()}</span>
                                                <span className={getStatusColor(c.status)}>{c.status.replace('_', ' ').toUpperCase()}</span>
                                            </div>
                                        </div>
                                        <Button
                                            size="sm"
                                            variant="secondary"
                                            onClick={() => handleDeleteComment(c.id)}
                                        >
                                            Delete
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>
                </div>
                 {user?.role === 'admin' && (
                     <Card title="Comment Management">
                         <Button variant="secondary" onClick={fetchAllComments} isLoading={isLoadingAll} className="mb-6 text-sm py-2 px-3 sm:text-base sm:py-3 sm:px-6">Refresh All</Button>
                         <select id="commentFilter" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="p-2 border border-border rounded-lg mb-6">
                             <option value="all">All</option>
                             <option value="open">Open</option>
                             <option value="in_progress">In Progress</option>
                             <option value="resolved">Resolved</option>
                             <option value="closed">Closed</option>
                         </select>
                         <div className="space-y-6 max-h-[80vh] overflow-y-auto pr-2">
                              {allComments.filter(c => filterStatus === 'all' || c.status === filterStatus).map(c => (
                                <div key={c.id} className="p-6 border border-white/20 rounded-lg frosted-glass-panel">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-bold text-white">{c.title}</h4>
                                            <p className="text-xs text-white/70">by {c.username} ({c.role}) on {new Date(c.created_at).toLocaleDateString()}</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <select id={`status-${c.id}`} value={c.status} onChange={(e) => handleUpdateStatus(c.id, e.target.value as any)} className="p-1 border border-white/30 rounded-md text-xs bg-white/20 text-white">
                                                <option value="open">Open</option>
                                                <option value="in_progress">In Progress</option>
                                                <option value="resolved">Resolved</option>
                                                <option value="closed">Closed</option>
                                            </select>
                                            <Button
                                                size="sm"
                                                variant="secondary"
                                                onClick={() => handleDeleteComment(c.id)}
                                            >
                                                Delete
                                            </Button>
                                        </div>
                                    </div>
                                    <p className="text-sm text-white/80 my-3 leading-relaxed">{c.description}</p>

                                    {/* Response Section */}
                                    {c.response ? (
                                        <div className="text-sm border-t border-border pt-2 mt-2">
                                            <b className="text-green-600">Response:</b> {c.response}
                                        </div>
                                    ) : (
                                        respondingTo === c.id ? (
                                            <div className="border-t border-border pt-2 mt-2">
                                                <textarea
                                                    id={`response-${c.id}`}
                                                    value={responseText}
                                                    onChange={(e) => setResponseText(e.target.value)}
                                                    placeholder="Type your response..."
                                                    className="w-full p-3 border border-border rounded-lg text-sm mb-3"
                                                    rows={4}
                                                />
                                                <div className="flex gap-2">
                                                    <Button
                                                        size="sm"
                                                        onClick={() => handleAddResponse(c.id)}
                                                        disabled={!responseText.trim() || !token}
                                                    >
                                                        Submit Response
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant="secondary"
                                                        onClick={() => setRespondingTo(null)}
                                                    >
                                                        Cancel
                                                    </Button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="border-t border-border pt-2 mt-2">
                                                <Button
                                                    size="sm"
                                                    variant="secondary"
                                                    onClick={() => startResponse(c.id)}
                                                >
                                                    Add Response
                                                </Button>
                                            </div>
                                        )
                                    )}
                                </div>
                            ))}
                        </div>
                    </Card>
                )}
            </div>
        </div>
    );
};

export default Comments;

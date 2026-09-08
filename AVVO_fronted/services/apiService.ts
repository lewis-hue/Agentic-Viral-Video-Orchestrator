
import { User, Comment, ChatMessage } from '../types';

const API_BASE_URL = '/api'; // Backend URL for local development with proxy

// --- API Service ---
export const apiService = {
    // Auth
    login: async (username: string, password: string): Promise<{ user: User, session_token: string }> => {
        console.log(`Attempting login for user: ${username}`);
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        if (!response.ok) {
            console.error('Login failed');
            throw new Error('Invalid credentials');
        }
        console.log('Login successful');
        return response.json();
    },

    checkSession: async (token: string): Promise<User | null> => {
        console.log('Checking session with token');
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) {
            console.error('Session check failed');
            return null;
        }
        console.log('Session check successful');
        return response.json();
    },

    logout: async (token: string): Promise<void> => {
        await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
        });
    },

    // Comments
    getComments: async (token: string): Promise<Comment[]> => {
        const response = await fetch(`${API_BASE_URL}/comments/`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch comments');
        return response.json();
    },

    getMyComments: async (token: string): Promise<Comment[]> => {
        const response = await fetch(`${API_BASE_URL}/comments/my`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch my comments');
        return response.json();
    },

    submitComment: async (token: string, data: Omit<Comment, 'id' | 'user_id' | 'username' | 'created_at' | 'status'>): Promise<Comment> => {
        const response = await fetch(`${API_BASE_URL}/comments/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to submit comment');
        return response.json();
    },

    updateComment: async (token: string, commentId: string, data: Partial<Comment>): Promise<Comment> => {
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to update comment');
        return response.json();
    },

    deleteComment: async (token: string, commentId: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to delete comment');
    },

    // Chat
    getChatMessages: async (token: string): Promise<ChatMessage[]> => {
        const response = await fetch(`${API_BASE_URL}/chat/messages`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch chat messages');
        return response.json();
    },

    sendChatMessage: async (token: string, message: string): Promise<ChatMessage> => {
        const response = await fetch(`${API_BASE_URL}/chat/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ message }),
        });
        if (!response.ok) throw new Error('Failed to send message');
        return response.json();
    },

    deleteChatMessage: async (token: string, messageId: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/chat/messages/${messageId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to delete message');
    },

    // Notifications
    getNotifications: async (token: string): Promise<any[]> => {
        const response = await fetch(`${API_BASE_URL}/notifications/`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch notifications');
        return response.json();
    },

    markNotificationRead: async (token: string, notificationId: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to mark notification as read');
    },

    markAllNotificationsRead: async (token: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/notifications/read-all`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to mark all notifications as read');
    },

    deleteNotification: async (token: string, notificationId: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to delete notification');
    },

    clearAllNotifications: async (token: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/notifications/`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to clear all notifications');
    },

    getOnlineUsers: async (token: string): Promise<any[]> => {
        const response = await fetch(`${API_BASE_URL}/notifications/online-users`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch online users');
        return response.json();
    },

    // Agents
    discoverTrends: async (token: string, data: { links: string[], voiceInput: string, files: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/trend-discovery`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to discover trends');
        return response.json();
    },

    getTrendStatus: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/trend-discovery/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get trend status');
        return response.json();
    },

    generateScript: async (token: string, data: { topic: string, instructions: string, voiceInput: string, files: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/story-ideation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to generate script');
        return response.json();
    },

    getScriptStatus: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/story-ideation/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get script status');
        return response.json();
    },

    refineScript: async (token: string, data: { topic: string, instructions: string, voiceInput: string, files: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/story-ideation/refine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to refine script');
        return response.json();
    },

    optimizeFeedback: async (token: string, data: { script: string, viral_video: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/optimization`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to optimize feedback');
        return response.json();
    },

    getOptimizationStatus: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/optimization/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get optimization status');
        return response.json();
    },

    generateVideo: async (token: string, data: { script: string, json_plan: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/video-generation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to generate video');
        return response.json();
    },

    getVideoGenerationStatusFromAgents: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/video-generation/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get video generation status');
        return response.json();
    },

    refineVideo: async (token: string, data: { script: string, json_plan: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/video-generation/refine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to refine video');
        return response.json();
    },

    downloadVideo: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/video-generation/download/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to download video');
        return response.json();
    },

    publishContent: async (token: string, data: { videos: string[], platforms: string[], caption: string, jsonPlan: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/publisher`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to publish content');
        return response.json();
    },

    getPublisherStatusFromAgents: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/publisher/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get publisher status');
        return response.json();
    },

    aiAssistant: async (token: string, data: { json_plan: string, instructions: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/ai-assistant`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to use AI assistant');
        return response.json();
    },

    getAgents: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get agents');
        return response.json();
    },

    // Dashboard
    getDashboardData: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/dashboard/`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get dashboard data');
        return response.json();
    },

    // Optimization
    getOptimizationData: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/optimization/`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get optimization data');
        return response.json();
    },

    analyzeContent: async (token: string, data: { script?: string, videoPath?: string, viralVideoUrl?: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/optimization/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to analyze content');
        return response.json();
    },

    // Knowledge Base
    getAllTips: async (token: string): Promise<any[]> => {
        const response = await fetch(`${API_BASE_URL}/knowledge/tips`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get tips');
        return response.json();
    },

    getTipsByCategory: async (token: string, category: string): Promise<any[]> => {
        const response = await fetch(`${API_BASE_URL}/knowledge/tips/${category}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get tips by category');
        return response.json();
    },

    getTipById: async (token: string, tipId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/knowledge/tip/${tipId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get tip by ID');
        return response.json();
    },

    // Video
    uploadVideo: async (token: string, file: File): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/video-uploader/api/videos/upload', {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to upload video');
        return response.json();
    },

    analyzeVideo: async (token: string, data: { user_video_path: string, reference_video: string, voice_input?: string, attached_files?: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/video/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to analyze video');
        return response.json();
    },

    attachFile: async (token: string, file: File): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE_URL}/video/attach`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to attach file');
        return response.json();
    },

    uploadAudio: async (token: string, file: File): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE_URL}/video/upload-audio`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to upload audio');
        return response.json();
    },

    transcribeAudio: async (token: string, data: { audio_path: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/video/transcribe`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to transcribe audio');
        return response.json();
    },

    generateVideoFromScript: async (token: string, data: { script: string, json_plan?: string, publish_request?: any, prompt?: string, aspect_ratio?: string, duration_seconds?: string, sample_count?: number, person_generation?: string, add_watermark?: boolean, include_rai_reason?: boolean, generate_audio?: boolean, resolution?: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/video/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to generate video');
        return response.json();
    },

    getVideoGenerationStatus: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/video/generate/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get video generation status');
        return response.json();
    },

    uploadAndPublish: async (token: string, file: File, data: { platforms: string[], title: string, description: string, publish_at?: string, captions?: any, voice_to_text?: boolean, tags?: string[] }): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('platforms', JSON.stringify(data.platforms));
        formData.append('title', data.title);
        formData.append('description', data.description);
        if (data.publish_at) formData.append('publish_at', data.publish_at);
        if (data.captions) formData.append('captions', JSON.stringify(data.captions));
        if (data.voice_to_text !== undefined) formData.append('voice_to_text', data.voice_to_text.toString());
        if (data.tags) formData.append('tags', JSON.stringify(data.tags));

        const response = await fetch('/video-uploader/upload-and-publish', {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to upload and publish');
        return response.json();
    },

    getPublishStatus: async (token: string, publishId: string): Promise<any> => {
        const response = await fetch(`/video-uploader/publish-status/${publishId}`, {
        });
        if (!response.ok) throw new Error('Failed to get publish status');
        return response.json();
    },

    getVideoHealth: async (token: string): Promise<any> => {
        const response = await fetch(`/video-uploader/health`, {
        });
        if (!response.ok) throw new Error('Failed to get video health');
        return response.json();
    },

    getAvailablePlatforms: async (token: string): Promise<any[]> => {
        const response = await fetch(`/video-uploader/platforms`, {
        });
        if (!response.ok) throw new Error('Failed to get available platforms');
        return response.json();
    },

    getSchedulerStatus: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/video/scheduler-status`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get scheduler status');
        return response.json();
    },

    trimVideo: async (token: string, data: { video_path: string, start_time: number, end_time: number, video_id: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/video/trim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to trim video');
        return response.json();
    },

    // Publisher
    publishContentViaPublisher: async (token: string, data: { videos: string[], platforms: string[], caption: string, jsonPayload: any }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/publisher/publish`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to publish content');
        return response.json();
    },

    getPublisherStatusFromPublisher: async (token: string, jobId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/publisher/status/${jobId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get publisher status');
        return response.json();
    },

    // Criticism
    criticizeContent: async (token: string, data: { content: string, voice_input?: string, attached_files?: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/criticism/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to criticize content');
        return response.json();
    },

    // Prompts
    generatePrompt: async (token: string, data: { topic: string, voice_input?: string, attached_files?: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/prompts/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to generate prompt');
        return response.json();
    },

    editPrompt: async (token: string, data: { topic: string, updated_prompt: string, voice_input?: string, attached_files?: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/prompts/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to edit prompt');
        return response.json();
    },

    // Simulation
    getSimulationData: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/simulation/`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get simulation data');
        return response.json();
    },

    // Collaboration endpoints
    // Auth endpoints for collaboration
    registerUser: async (data: { username: string, email: string, password: string, role: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to register user');
        return response.json();
    },

    loginUser: async (data: { username: string, password: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to login');
        return response.json();
    },

    logoutUser: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to logout');
        return response.json();
    },

    getCurrentUser: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get current user');
        return response.json();
    },

    // User management (Admin only)
    getAllUsers: async (token: string): Promise<any[]> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/users`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get users');
        return response.json();
    },

    getUser: async (token: string, userId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/users/${userId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get user');
        return response.json();
    },

    updateUser: async (token: string, userId: number, data: { username?: string, email?: string, is_active?: boolean }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to update user');
        return response.json();
    },

    deleteUser: async (token: string, userId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to delete user');
        return response.json();
    },

    // Video management
    createVideo: async (token: string, data: { title: string, description?: string, privacy: string, tags?: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/videos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to create video');
        return response.json();
    },

    getVideos: async (token: string, privacyFilter?: string): Promise<any[]> => {
        const url = privacyFilter ? `${API_BASE_URL}/collaboration/videos?privacy_filter=${privacyFilter}` : `${API_BASE_URL}/collaboration/videos`;
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get videos');
        return response.json();
    },

    getVideo: async (token: string, videoId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/videos/${videoId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get video');
        return response.json();
    },

    updateVideo: async (token: string, videoId: number, data: { title?: string, description?: string, privacy?: string, tags?: string[] }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/videos/${videoId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to update video');
        return response.json();
    },

    deleteVideo: async (token: string, videoId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/videos/${videoId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to delete video');
        return response.json();
    },

    bulkVideoOperation: async (token: string, data: { video_ids: number[], operation: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/videos/bulk`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to perform bulk operation');
        return response.json();
    },

    // Analytics
    getUserAnalytics: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/analytics/users`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get user analytics');
        return response.json();
    },

    getVideoAnalytics: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/analytics/videos`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get video analytics');
        return response.json();
    },

    // Feedback system
    createFeedback: async (token: string, data: { title: string, description: string, category: string, priority?: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to create feedback');
        return response.json();
    },

    getAllFeedback: async (token: string): Promise<any[]> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/feedback`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get feedback');
        return response.json();
    },

    getMyFeedback: async (token: string): Promise<any[]> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/feedback/my`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get my feedback');
        return response.json();
    },

    getFeedback: async (token: string, feedbackId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/feedback/${feedbackId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get feedback');
        return response.json();
    },

    updateFeedback: async (token: string, feedbackId: number, data: { status?: string, assigned_to?: number, implementation_notes?: string, version_implemented?: string }): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/feedback/${feedbackId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Failed to update feedback');
        return response.json();
    },

    deleteFeedback: async (token: string, feedbackId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/feedback/${feedbackId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to delete feedback');
        return response.json();
    },

    getFeedbackStats: async (token: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/collaboration/feedback/stats`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to get feedback stats');
        return response.json();
    }
};

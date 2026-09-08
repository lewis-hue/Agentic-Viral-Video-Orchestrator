
export type Page = 'home' | 'trend-discovery' | 'story-ideation' | 'video-generation' | 'optimization-feedback' | 'publisher' | 'documentation' | 'comments' | 'chat';

export interface User {
    id: number;
    username: string;
    email: string;
    role: 'admin' | 'ai_engineer' | 'marketing_designer';
    created_at: string;
    token?: string;
}

export interface ChatUser {
    id: number;
    username: string;
    role: string;
}

export interface Comment {
    id: string;
    user_id: number;
    username: string;
    role?: string;
    title: string;
    description: string;
    category: 'feature' | 'bug' | 'improvement' | 'ui' | 'performance';
    priority: 'low' | 'medium' | 'high' | 'critical';
    status: 'open' | 'in_progress' | 'resolved' | 'closed' | 'deleted';
    created_at: string;
    response?: string;
}

export interface ChatMessage {
    id: string;
    user_id: number;
    username: string;
    role?: string;
    message: string;
    status: 'active' | 'deleted';
    timestamp: string;
}

export interface Trend {
    theme: string;
    description: string;
    key_elements: string[];
    virality_score: number;
    reasoning: string;
    additional_instructions: {
        hook: string;
        style: string;
        tone: string;
    };
}

export interface LogEntry {
    level: 'INFO' | 'SUCCESS' | 'ERROR';
    message: string;
    timestamp: string;
}

export interface Notification {
    id: string;
    type: 'new_comment' | 'new_chat' | 'failed_task' | 'successful_task' | 'version_update' | 'document_change';
    title: string;
    message: string;
    read: boolean;
    timestamp: string;
    action_url?: string;
}

export interface OnlineUser {
    user_id: number;
    username: string;
    role: string;
    last_seen: string;
}

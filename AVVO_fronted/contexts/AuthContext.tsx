
import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { User } from '../types';
import { apiService } from '../services/apiService';

interface AuthContextType {
    user: User | null;
    token: string | null;
    loading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('sessionToken'));
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const initAuth = async () => {
            if (token && token.trim()) {
                const currentUser = await apiService.checkSession(token);
                if (currentUser) {
                    setUser(currentUser);
                } else {
                    // Invalid or expired session
                    localStorage.removeItem('sessionToken');
                    setToken(null);
                    setUser(null);
                }
            } else {
                setUser(null);
            }
            setLoading(false);
        };
        initAuth();
    }, [token]);
    

    const login = async (username: string, password: string) => {
        const { user: loggedInUser, session_token } = await apiService.login(username, password);
        setUser(loggedInUser);
        setToken(session_token);
        localStorage.setItem('sessionToken', session_token);
    };

    const logout = async () => {
        await apiService.logout(token!);
        setUser(null);
        setToken(null);
        localStorage.removeItem('sessionToken');
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

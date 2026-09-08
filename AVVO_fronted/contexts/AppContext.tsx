
import React, { createContext, useState, useContext, ReactNode, useCallback, useMemo } from 'react';
import { LogEntry, Trend } from '../types';

interface AppContextType {
    generatedScript: string;
    setGeneratedScript: (script: string) => void;
    generatedVideoPath: string;
    setGeneratedVideoPath: (path: string) => void;
    currentTrends: Trend[];
    setCurrentTrends: (trends: Trend[]) => void;
    logs: LogEntry[];
    addLog: (level: 'INFO' | 'SUCCESS' | 'ERROR', message: string) => void;
    clearLogs: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [generatedScript, setGeneratedScript] = useState('');
    const [generatedVideoPath, setGeneratedVideoPath] = useState('');
    const [currentTrends, setCurrentTrends] = useState<Trend[]>([]);
    const [logs, setLogs] = useState<LogEntry[]>([{
        level: 'INFO',
        message: 'VIRALISH system initialized. Awaiting user input.',
        timestamp: new Date().toLocaleTimeString()
    }]);

    const addLog = useCallback((level: 'INFO' | 'SUCCESS' | 'ERROR', message: string) => {
        const newLog: LogEntry = {
            level,
            message,
            timestamp: new Date().toLocaleTimeString(),
        };
        setLogs(prevLogs => [newLog, ...prevLogs]);
    }, []);

    const clearLogs = useCallback(() => {
        setLogs([]);
        addLog('INFO', 'System logs cleared.');
    }, [addLog]);

    const contextValue = useMemo(() => ({
        generatedScript,
        setGeneratedScript,
        generatedVideoPath,
        setGeneratedVideoPath,
        currentTrends,
        setCurrentTrends,
        logs,
        addLog,
        clearLogs
    }), [generatedScript, generatedVideoPath, currentTrends, logs, addLog, clearLogs]);

    return (
        <AppContext.Provider value={contextValue}>
            {children}
        </AppContext.Provider>
    );
};

export const useApp = (): AppContextType => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
};

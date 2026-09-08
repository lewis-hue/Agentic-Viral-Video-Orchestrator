
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import TrendDiscovery from './pages/TrendDiscovery';
import StoryIdeation from './pages/StoryIdeation';
import VideoGeneration from './pages/VideoGeneration';
import OptimizationFeedback from './pages/OptimizationFeedback';
import Publisher from './pages/Publisher';
import Documentation from './pages/Documentation';
import Comments from './pages/Comments';
import Chat from './pages/Chat';
import Login from './pages/Login';
import { AppProvider } from './contexts/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { Page } from './types';

const AppContent: React.FC = () => {
    const location = useLocation();
    const { user, loading } = useAuth();

    const pathToPage: Record<string, Page> = {
        '/': 'home',
        '/trend-discovery': 'trend-discovery',
        '/story-ideation': 'story-ideation',
        '/video-generation': 'video-generation',
        '/optimization-feedback': 'optimization-feedback',
        '/publisher': 'publisher',
        '/documentation': 'documentation',
        '/comments': 'comments',
        '/chat': 'chat',
    };

    const activePage = pathToPage[location.pathname] || 'home';

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
                <div className="relative">
                    <div className="w-20 h-20 border-4 border-blue-300/30 rounded-full animate-spin"></div>
                    <div className="absolute top-0 left-0 w-20 h-20 border-4 border-transparent border-t-blue-400 rounded-full animate-spin"></div>
                    <div className="absolute top-0 left-0 w-20 h-20 border-4 border-transparent border-t-blue-500 rounded-full animate-spin animation-delay-300"></div>
                    <div className="flex items-center justify-center w-20 h-20">
                        <span className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-blue-600 bg-clip-text text-transparent">
                            AVVO
                        </span>
                    </div>
                </div>
            </div>
        );
    }
    
    if (!user) {
        return <Login />;
    }


    return (
        <div className="flex flex-col h-screen bg-gradient-to-br from-blue-25 via-white to-blue-50 text-blue-800">
            <Header activePage={activePage} />
            <main className="flex-grow p-6 md:p-12 overflow-y-auto relative">
                {/* Subtle background elements */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-blue-300/15 to-blue-400/10 rounded-full"></div>
                    <div className="absolute top-40 right-32 w-24 h-24 bg-gradient-to-br from-blue-400/15 to-blue-500/10 rounded-full"></div>
                    <div className="absolute bottom-32 left-1/4 w-20 h-20 bg-gradient-to-br from-blue-200/15 to-blue-300/10 rounded-full"></div>
                </div>
                <div className="relative">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/trend-discovery" element={<TrendDiscovery />} />
                        <Route path="/story-ideation" element={<StoryIdeation />} />
                        <Route path="/video-generation" element={<VideoGeneration />} />
                        <Route path="/optimization-feedback" element={<OptimizationFeedback />} />
                        <Route path="/publisher" element={<Publisher />} />
                        <Route path="/documentation" element={<Documentation />} />
                        <Route path="/comments" element={<Comments />} />
                        <Route path="/chat" element={<Chat />} />
                    </Routes>
                </div>
            </main>
        </div>
    );
}


const App: React.FC = () => {
    return (
        <BrowserRouter>
            <AuthProvider>
                <NotificationProvider>
                    <AppProvider>
                        <AppContent />
                    </AppProvider>
                </NotificationProvider>
            </AuthProvider>
        </BrowserRouter>
    );
};

export default App;

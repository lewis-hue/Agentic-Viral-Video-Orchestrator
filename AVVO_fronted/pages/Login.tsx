
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/Button';

const Login: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    
    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!username || !password) {
            setError('Please enter both username and password.');
            return;
        }
        setError('');
        setIsLoading(true);
        try {
            await login(username, password);
        } catch (err: any) {
            setError(err.message || 'Login failed. Please try again.');
            setIsLoading(false);
        }
    };

    return (
        <main className="flex justify-center items-center min-h-screen p-4 relative overflow-hidden" style={{
            backgroundImage: 'url(/images/login-bg.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed',
            filter: 'brightness(1.1) contrast(1.2) saturate(1.4) hue-rotate(5deg)'
        }}>
            {/* Subtle background overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-300/15 via-transparent to-blue-200/15"></div>

            {/* Main title with light pink theme */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <h1 className="text-7xl font-black bg-gradient-to-r from-blue-400 via-white to-blue-300 bg-clip-text text-transparent drop-shadow-2xl">
                    AVVO
                </h1>
            </div>

            {/* Login form with glass morphism effect */}
            <div className="relative z-10 frosted-glass-panel rounded-3xl p-10 shadow-2xl max-w-md w-full text-center border border-white/20 hover:bg-white/15 transition-all duration-500">
                {/* Logo and title section */}
                <div className="flex justify-center items-center gap-4 mb-10">
                    <div className="icon-container">
                        <svg viewBox="0 0 24 24" fill="currentColor" className="w-16 h-16 text-blue-400">
                            <path d="M12,2A10,10,0,1,0,22,12,10,10,0,0,0,12,2ZM10,16.5v-9l6,4.5Z"></path>
                        </svg>
                    </div>
                    <h1 className="text-5xl font-black bg-gradient-to-r from-blue-500 via-blue-400 to-blue-600 bg-clip-text text-transparent">
                        AVVO
                    </h1>
                </div>


                <form onSubmit={handleLogin} className="text-left space-y-6">
                    <div>
                        <label htmlFor="loginUsername" className="block text-sm font-semibold text-white/80 mb-2">
                            Username
                        </label>
                        <input
                            type="text"
                            id="loginUsername"
                            placeholder="Enter 'admin', 'ai_engineer', or 'marketing_designer'"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full p-4 border-2 border-blue-300/30 rounded-xl bg-white/20 backdrop-blur-sm text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors duration-200 hover:bg-white/25"
                        />
                    </div>
                    <div>
                        <label htmlFor="loginPassword" className="block text-sm font-semibold text-white/80 mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            id="loginPassword"
                            placeholder="Enter 'admin123', 'ai_engineer123', or 'marketing123'"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full p-4 border-2 border-blue-300/30 rounded-xl bg-white/20 backdrop-blur-sm text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors duration-200 hover:bg-white/25"
                        />
                    </div>
                    {error && (
                        <div className="text-red-300 text-sm text-center leading-relaxed bg-red-500/20 border border-red-300/30 rounded-lg p-3 backdrop-blur-sm">
                            {error}
                        </div>
                    )}
                    <div className="flex justify-center mt-8" style={{ marginLeft: '1.45rem' }}>
                        <Button type="submit" isLoading={isLoading} className="text-lg py-4 px-4 border-2 border-blue-300/30 rounded-xl">
                           Login to AVVO
                        </Button>
                    </div>
                </form>
            </div>

            {/* Floating accent elements */}
            <div className="absolute top-10 left-10 w-20 h-20 bg-gradient-to-br from-blue-300 to-blue-400 rounded-full opacity-15"></div>
            <div className="absolute bottom-10 right-10 w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-500 rounded-full opacity-15"></div>
            <div className="absolute top-1/2 right-20 w-12 h-12 bg-gradient-to-br from-blue-200 to-blue-300 rounded-full opacity-15"></div>
        </main>
    );
};

export default Login;

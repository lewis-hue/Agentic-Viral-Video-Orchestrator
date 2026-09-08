import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { NAV_ITEMS } from '../constants';
import { Page } from '../types';
import TeamPresence from './TeamPresence';
import NotificationCenter from './NotificationCenter';

interface HeaderProps {
    activePage: Page;
}

const Header: React.FC<HeaderProps> = ({ activePage }) => {
    const { user, logout } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsMenuOpen(false);
            }
        };

        if (isMenuOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isMenuOpen]);

    return (
        <header className="flex items-center justify-between w-full bg-gradient-to-r from-white/95 via-blue-50/90 to-blue-100/85 backdrop-blur-xl p-4 border-b border-blue-200/60 shadow-lg z-40">
            {/* Logo and Brand Section */}
            <div className="flex items-center gap-3">
                <div className="icon-container">
                    <svg viewBox="0 0 24 24" fill="currentColor" className="w-10 h-10 text-blue-400">
                        <path d="M12,2A10,10,0,1,0,22,12,10,10,0,0,0,12,2ZM10,16.5v-9l6,4.5Z"></path>
                    </svg>
                </div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 bg-clip-text text-transparent">
                    AVVO
                </h1>
            </div>

            {/* Right Section with Menu, Presence, and Notifications */}
            <div className="flex items-center gap-4">
                {/* Team Presence */}
                <div className="icon-container">
                    <TeamPresence />
                </div>

                {/* Notifications */}
                <div className="icon-container">
                    <NotificationCenter />
                </div>

                {/* Hamburger Menu */}
                <div className="relative z-50" ref={menuRef}>
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="p-3 text-blue-500 hover:text-blue-400 transition-colors duration-200 bg-white/50 rounded-lg hover:bg-white/70"
                    >
                        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
                        </svg>
                    </button>

                    {/* Ultra-Vibrant Dropdown Menu */}
                    {isMenuOpen && (
                        <div className="absolute right-0 mt-3 w-72 frosted-glass-panel border-2 border-blue-200/60 rounded-2xl shadow-2xl z-50">
                            <nav className="p-6">
                                <ul className="space-y-3">
                                    {NAV_ITEMS.map(item => {
                                        const path = item.id === 'home' ? '/' : `/${item.id}`;
                                        return (
                                            <li key={item.id}>
                                                <Link
                                                    to={path}
                                                    onClick={() => setIsMenuOpen(false)}
                                                    className={`flex items-center py-3 px-4 rounded-xl font-semibold transition-colors duration-200 cursor-pointer ${
                                                        activePage === item.id
                                                            ? 'bg-gradient-to-r from-blue-400 to-blue-500 text-white shadow-lg'
                                                            : 'text-blue-700 hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100 hover:text-blue-800'
                                                    }`}
                                                >
                                                    <span className="w-5 h-5 mr-4 text-blue-500"><item.icon /></span>
                                                    {item.label}
                                                </Link>
                                            </li>
                                        );
                                    })}
                                </ul>
                            </nav>
                            <div className="border-t border-blue-200/60 p-6 bg-gradient-to-r from-blue-50/80 to-blue-100/70">
                                <div className="mb-4">
                                    <p className="font-bold text-lg text-blue-800">{user?.username}</p>
                                    <p className="text-sm text-blue-600">{user?.email}</p>
                                </div>
                                <button
                                    onClick={() => logout()}
                                    className="w-full text-sm font-bold text-center text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 py-3 rounded-xl transition-colors duration-200 shadow-lg"
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;
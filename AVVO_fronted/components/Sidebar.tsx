
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { NAV_ITEMS } from '../constants';
import { Page } from '../types';

interface SidebarProps {
    activePage: Page;
    setActivePage: (page: Page) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activePage, setActivePage }) => {
    const { user, logout } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    return (
        <div className="relative">
            <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2 text-text-light hover:text-text">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
            </button>
            {isMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-card border border-border rounded-lg shadow-lg z-50">
                    <nav className="p-4">
                        <ul className="space-y-2">
                            {NAV_ITEMS.map(item => (
                                <li key={item.id}>
                                    <a
                                        href="#"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            setActivePage(item.id);
                                            setIsMenuOpen(false);
                                        }}
                                        className={`flex items-center py-2 px-3 rounded-lg font-medium transition-all duration-200 ${
                                            activePage === item.id
                                            ? 'bg-primary text-white'
                                            : 'text-text-light hover:bg-secondary'
                                        }`}
                                    >
                                        <span className="w-4 h-4 mr-3"><item.icon /></span>
                                        {item.label}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </nav>
                    <div className="border-t border-border p-4">
                        <div className="mb-3">
                            <p className="font-bold text-text">{user?.username}</p>
                            <p className="text-sm text-text-light">{user?.email}</p>
                        </div>
                        <button onClick={() => logout()} className="w-full text-sm font-semibold text-center text-error bg-error bg-opacity-10 hover:bg-opacity-20 py-2 rounded-md transition-colors duration-200">
                            Logout
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Sidebar;

import React from 'react';
import { Link } from 'react-router-dom';

const BackButton: React.FC = () => {
    return (
        <Link
            to="/"
            className="flex items-center gap-2 mb-4 py-2 px-4 bg-secondary text-text-light hover:bg-gray-200 hover:text-text rounded-lg transition-all duration-200"
        >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back to Home
        </Link>
    );
};

export default BackButton;
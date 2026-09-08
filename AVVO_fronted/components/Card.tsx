
import React from 'react';

interface CardProps {
    title: string;
    children: React.ReactNode;
    className?: string;
}

const Card: React.FC<CardProps> = ({ title, children, className = '' }) => {
    return (
        <div className={`bg-background rounded-xl p-6 shadow-custom border border-transparent hover:border-primary/20 hover:shadow-custom-hover transition-all duration-300 ${className}`}>
            <h2 className="text-xl font-semibold mb-4 pb-3 border-b border-border flex items-center gap-2">
                 <span className="w-1 h-5 bg-gradient-to-br from-primary to-primary-hover rounded-full"></span>
                {title}
            </h2>
            {children}
        </div>
    );
};

export default Card;

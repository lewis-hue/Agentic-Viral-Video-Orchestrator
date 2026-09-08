
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
    children: React.ReactNode;
    icon?: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
    variant = 'primary',
    size = 'md',
    isLoading = false,
    children,
    className = '',
    icon,
    ...props
}) => {
    const sizeClasses = {
        sm: "py-1 px-2 text-xs",
        md: "py-2 px-4 text-sm sm:py-3 sm:px-6 sm:text-base",
        lg: "py-3 px-6 text-base"
    };

    const baseClasses = `${sizeClasses[size]} font-semibold rounded-lg border focus:outline-none focus:ring-4 transition-all duration-200 inline-flex items-center justify-center gap-2 relative overflow-hidden disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none`;

    const variantClasses = {
          primary: "bg-accent text-white border-transparent shadow-lg shadow-accent/30 hover:shadow-xl hover:shadow-accent/40 hover:-translate-y-0.5 active:translate-y-0 focus:ring-accent/30",
          secondary: "bg-secondary text-text border-border hover:bg-blue-50 hover:border-blue-200 hover:-translate-y-px active:translate-y-0 focus:ring-blue-200",
      };

    return (
        <button 
            className={`${baseClasses} ${variantClasses[variant]} ${className}`}
            disabled={isLoading || props.disabled}
            {...props}
        >
            {isLoading && <span className="w-5 h-5 border-2 border-white border-b-transparent rounded-full animate-spin"></span>}
            {!isLoading && icon}
            <span>{children}</span>
        </button>
    );
};

export default Button;

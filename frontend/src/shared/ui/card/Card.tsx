import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className, onClick }) => {
  return (
    <div
      className={`bg-gray-800 rounded-lg border border-gray-700 p-4 ${onClick ? 'cursor-pointer hover:border-gray-600 transition-colors' : ''} ${className || ''}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

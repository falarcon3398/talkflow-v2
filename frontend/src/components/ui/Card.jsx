import React from 'react';

const Card = ({ children, className = '', interactive = false, ...props }) => {
  return (
    <div 
      className={`${interactive ? 'interactive-card' : 'glass-card'} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;

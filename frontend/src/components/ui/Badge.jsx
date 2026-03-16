import React from 'react';

const Badge = ({ children, variant = 'primary', className = '' }) => {
  const variants = {
    primary: 'badge-primary',
    success: 'badge-success',
    danger: 'bg-red-100 text-red-700',
    warning: 'bg-amber-100 text-amber-700',
  };

  return (
    <span className={`${variants[variant] || variants.primary} ${className}`}>
      {children}
    </span>
  );
};

export default Badge;

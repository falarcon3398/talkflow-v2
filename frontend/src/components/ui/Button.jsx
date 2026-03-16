import React from 'react';

const Button = ({ 
  children, 
  variant = 'primary', 
  className = '', 
  icon: Icon,
  disabled = false,
  ...props 
}) => {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    ghost: 'btn-ghost',
    danger: 'btn-danger',
  };

  return (
    <button
      disabled={disabled}
      className={`${variants[variant] || variants.primary} ${className}`}
      {...props}
    >
      {Icon && <span className="text-lg">{Icon}</span>}
      {children}
    </button>
  );
};

export default Button;

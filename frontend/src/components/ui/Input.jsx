import React from 'react';

const Input = ({ label, error, className = '', ...props }) => {
  return (
    <div className="w-full space-y-1">
      {label && <label className="input-label">{label}</label>}
      <input 
        className={`input-base ${error ? 'border-red-500 focus:ring-red-500/10' : ''} ${className}`}
        {...props}
      />
      {error && <p className="text-[10px] font-bold text-red-500 uppercase">{error}</p>}
    </div>
  );
};

export default Input;

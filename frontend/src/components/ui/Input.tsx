import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
  children?: React.ReactNode;
}

export function Input({ icon, className = '', children, ...props }: InputProps) {
  return (
    <div className={`relative w-full flex flex-col sm:flex-row gap-sm glass-input p-2 rounded-xl shadow-2xl shadow-black/50 ${className}`}>
      <div className="flex-grow flex items-center px-4 w-full">
        {icon && <span className="text-outline-variant mr-3 flex items-center">{icon}</span>}
        <input
          className="w-full bg-transparent border-none text-on-surface font-mono-code text-body-md placeholder:text-outline-variant focus:ring-0 px-0 py-4 outline-none"
          {...props}
        />
      </div>
      {children}
    </div>
  );
}

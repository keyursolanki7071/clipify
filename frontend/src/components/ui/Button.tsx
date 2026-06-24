import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost';
  children: React.ReactNode;
}

export function Button({ variant = 'primary', children, className = '', ...props }: ButtonProps) {
  const baseClasses = "px-8 py-4 rounded-lg font-headline-lg-mobile text-[16px] font-bold flex items-center justify-center gap-2 whitespace-nowrap active:scale-95 transition-transform duration-200";
  
  const variants = {
    primary: "btn-primary-gradient",
    ghost: "bg-transparent border border-white/10 hover:border-primary/50 text-on-surface-variant hover:text-primary"
  };

  return (
    <button className={`${baseClasses} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

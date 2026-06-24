import React from 'react';

interface ChipProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: React.ReactNode;
  active?: boolean;
  children: React.ReactNode;
}

export function Chip({ icon, active, children, className = '', ...props }: ChipProps) {
  return (
    <button
      className={`chip-selectable flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 font-label-sm text-label-sm ${
        active 
          ? 'active border-transparent' 
          : 'bg-surface/30 text-on-surface-variant'
      } ${className}`}
      {...props}
    >
      {icon && <span className="flex items-center text-[16px]">{icon}</span>}
      {children}
    </button>
  );
}

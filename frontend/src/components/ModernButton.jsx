import React from 'react';

// Componente reutilizável para botões modernos
const ModernButton = ({ children, className = '', ...props }) => (
  <button
    className={
      `w-full md:w-auto px-4 py-2 rounded-lg bg-primary text-white font-semibold shadow-lg hover:bg-primary/90 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50 ` + className
    }
    {...props}
  >
    {children}
  </button>
);

export default ModernButton;

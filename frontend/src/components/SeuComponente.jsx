import React from 'react';
import ModernButton from './ModernButton';

const SeuComponente = () => (
  <div className="bg-white shadow-lg rounded-xl p-4 space-y-4 max-w-md mx-auto">
    <h2 className="text-xl font-bold text-gray-900 leading-relaxed">Título</h2>
    <p className="text-base text-gray-600 leading-relaxed">
      Descrição do componente.
    </p>
    <div className="flex flex-col md:flex-row gap-3">
      <ModernButton>Confirmar</ModernButton>
      <ModernButton className="bg-gray-200 text-gray-800 hover:bg-gray-300">Cancelar</ModernButton>
    </div>
  </div>
);

export default SeuComponente;

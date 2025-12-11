import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import RoleBasedRoute from './components/RoleBasedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// Componente para proteger rotas com bloqueio de roles
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <RoleBasedRoute blockedRoles={['ROOT', 'GESTOR']}>
      {children}
    </RoleBasedRoute>
  );
};

// Componente principal da aplicação
const AppContent: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/entidades" element={<div>Entidades - Em desenvolvimento</div>} />
                  <Route path="/usuarios" element={<div>Usuários - Em desenvolvimento</div>} />
                  <Route path="/fornecedores" element={<div>Fornecedores - Em desenvolvimento</div>} />
                  <Route path="/contratos" element={<div>Contratos - Em desenvolvimento</div>} />
                  <Route path="/auditoria" element={<div>Auditoria - Em desenvolvimento</div>} />
                  <Route path="/relatorios" element={<div>Relatórios - Em desenvolvimento</div>} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

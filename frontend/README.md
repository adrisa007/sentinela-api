# Sentinela Frontend

Frontend React + Vite para o sistema de gestão de contratos e fiscalização.

## 🚀 Tecnologias

- **React 19** - Framework JavaScript
- **Vite** - Build tool e dev server
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Framework CSS utilitário
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **Lucide React** - Ícones

## 📱 Características

- **Mobile-first** - Design responsivo otimizado para mobile
- **Autenticação JWT** - Sistema de login seguro
- **API Integration** - Integração completa com backend FastAPI
- **TypeScript** - Tipagem completa para melhor DX
- **Tailwind CSS** - Estilização moderna e consistente

## 🏃‍♂️ Como executar

### Pré-requisitos

- Node.js 18+
- Backend rodando em `http://localhost:8000`

### Instalação

```bash
# Instalar dependências
npm install

# Executar em modo desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

### Build para produção

```bash
npm run build
npm run preview
```

## 📁 Estrutura do Projeto

```
src/
├── components/     # Componentes reutilizáveis
├── contexts/       # Contextos React (Auth, etc.)
├── pages/         # Páginas da aplicação
├── services/      # Serviços (API, etc.)
├── types/         # Tipos TypeScript
├── utils/         # Utilitários
└── hooks/         # Custom hooks
```

## 🔐 Autenticação

### Credenciais de teste

- **Admin**: `admin@sentinela.app` / `admin123`
- **Gestor**: `gestor@entidade.com` / `gestor123`

## 📡 API

O frontend se conecta automaticamente com o backend em `http://localhost:8000`.

### Endpoints principais

- `POST /auth/login` - Autenticação
- `GET /auth/me` - Usuário atual
- `GET /entidades` - Lista entidades
- `GET /usuarios` - Lista usuários
- `GET /fornecedores` - Lista fornecedores
- `GET /contratos` - Lista contratos
- `GET /pncp/fornecedor/validar/{cnpj}` - Validar fornecedor PNCP

## 🎨 Design System

### Cores principais

- **Primary**: Blue (`blue-600`, `blue-500`)
- **Success**: Green (`green-500`)
- **Warning**: Orange/Yellow
- **Error**: Red (`red-600`)

### Breakpoints

- **Mobile**: `< 768px`
- **Tablet**: `768px - 1024px`
- **Desktop**: `> 1024px`

## 📱 Mobile-First

O design é otimizado para mobile primeiro, com:

- Navegação por drawer no mobile
- Layout responsivo
- Toque-friendly buttons
- Tipografia escalável

## 🔧 Desenvolvimento

### Scripts disponíveis

```bash
npm run dev      # Servidor de desenvolvimento
npm run build    # Build para produção
npm run lint     # Executar ESLint
npm run preview  # Preview do build
```

### Estrutura de commits

Seguimos conventional commits:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação
- `refactor:` - Refatoração
- `test:` - Testes
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

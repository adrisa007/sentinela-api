# Teste do bloqueio ROOT/GESTOR

## Cenários de teste:

### ✅ Usuários permitidos (devem conseguir fazer login):
- FISCAL_TECNICO
- FISCAL_ADM  
- APOIO
- AUDITOR

### ❌ Usuários bloqueados (devem ser impedidos):
- ROOT
- GESTOR

## Como testar:

1. Tentar fazer login com usuário ROOT ou GESTOR
2. Verificar se aparece mensagem: 'Acesso negado: Usuários com perfil ROOT ou GESTOR não podem acessar o sistema através desta interface.'
3. Verificar se o usuário é automaticamente deslogado após a tentativa

## Credenciais de teste disponíveis:
- Admin (ROOT): admin@sentinela.app / admin123 ❌ BLOQUEADO
- Gestor: gestor@entidade.com / gestor123 ❌ BLOQUEADO

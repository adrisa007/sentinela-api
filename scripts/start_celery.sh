#!/bin/bash

# Script para iniciar os serviços do Celery localmente

echo "Iniciando Celery Worker..."
celery -A app.core.celery_app worker --loglevel=info &

echo "Iniciando Celery Beat..."
celery -A app.core.celery_app beat --loglevel=info &

echo "Serviços do Celery iniciados. Pressione Ctrl+C para parar."

# Aguardar os processos
wait
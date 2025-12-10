from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "sentinela_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.beat_schedule = {
    # Exemplo: backup diário às 2h
    "backup-diario": {
        "task": "app.tasks.backup_diario",
        "schedule": crontab(hour=2, minute=0),
    },
    # Exemplo: alerta a cada hora
    "alertas": {
        "task": "app.tasks.enviar_alertas",
        "schedule": crontab(minute=0, hour="*"),
    },
    # Exemplo: sync PNCP todo dia às 3h
    "pncp-sync": {
        "task": "app.tasks.sync_pncp",
        "schedule": crontab(hour=3, minute=0),
    },
}

celery_app.conf.timezone = "America/Sao_Paulo"

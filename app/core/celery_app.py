from celery import Celery
import os
from app.core.config import settings

# Configuração do Celery
celery_app = Celery(
    "sentinela_api",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.tasks"]
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.*": {"queue": "sentinela"},
    },
    beat_schedule={
        # Tarefas agendadas podem ser definidas aqui
        # "cleanup-old-audits": {
        #     "task": "app.tasks.cleanup_old_audits",
        #     "schedule": crontab(hour=2, minute=0),  # Todos os dias às 2:00
        # },
    }
)

# Configuração para desenvolvimento
if os.getenv("ENVIRONMENT") == "development":
    celery_app.conf.update(
        task_always_eager=False,
        task_eager_propagates=True,
    )
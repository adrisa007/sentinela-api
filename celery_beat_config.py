from celery import Celery
from celery.schedules import crontab
import os

# Configuração do Celery Beat
beat_schedule = {
    # Exemplo de tarefa agendada - limpeza de auditorias antigas
    "cleanup-old-audits": {
        "task": "app.tasks.tasks.cleanup_old_audits",
        "schedule": crontab(hour=2, minute=0),  # Todos os dias às 2:00
    },
    # Outras tarefas agendadas podem ser adicionadas aqui
    # "generate-monthly-reports": {
    #     "task": "app.tasks.tasks.generate_monthly_reports",
    #     "schedule": crontab(day_of_month=1, hour=6, minute=0),  # Primeiro dia do mês às 6:00
    # },
}

# Configurações adicionais do Celery Beat
beat_timezone = "UTC"
beat_max_loop_interval = 300  # 5 minutos
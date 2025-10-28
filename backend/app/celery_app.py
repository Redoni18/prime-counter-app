"""Celery application configuration."""
import os
from celery import Celery

REDIS_URL = os.getenv('CELERY_BROKER_URL')
RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

celery_app = Celery(
    'datafuse',
    broker=REDIS_URL,
    backend=RESULT_BACKEND,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600
)

celery_app.conf.task_default_retry_delay = 30
celery_app.conf.task_max_retries = 3

if __name__ == '__main__':
    celery_app.start()



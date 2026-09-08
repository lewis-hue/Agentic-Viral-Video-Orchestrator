from celery import Celery
import os

celery_app = Celery('app')

celery_app.conf.broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app.conf.result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = 3600
celery_app.conf.worker_pool = 'gevent'  # For async tasks

# Import tasks to register them with Celery
from app import tasks
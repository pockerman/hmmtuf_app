import os
from celery import Celery
from django.conf import settings
from .celery_settings import CELERY_RESULT_BACKEND, CELERY_TASK_SERIALIZER, CELERY_RESULT_SERIALIZER

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hmmtuf.settings')

celery_app = Celery('hmmtuf',
                    backend=CELERY_RESULT_BACKEND,
                    task_serializer=CELERY_TASK_SERIALIZER,
                    result_serializer=CELERY_RESULT_SERIALIZER)
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
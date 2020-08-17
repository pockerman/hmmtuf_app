# make sure that we start celery_app
# when start our application
from .celery import celery_app as celery_app
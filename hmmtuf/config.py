from .celery_settings import BROKER_URL
from .celery_settings import CELERY_RESULT_BACKEND
from .celery_settings import CELERY_ACCEPT_CONTENT
from .celery_settings import CELERY_TASK_SERIALIZER
from .celery_settings import CELERY_RESULT_SERIALIZER
from .celery_settings import CELERY_TIMEZONE

REMOTE = False

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
USE_CELERY = True

# used when USE_CELERY = False
NUM_WORKER_PROCESSES = 2
MAX_QUEUE_JOB_SIZE = 20

if REMOTE == True:
    BASE_DIR = '/home/a/ag568/hmmtuf_app'

    # Database
    # https://docs.djangoproject.com/en/3.1/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR + '/' + 'db.sqlite3',
        }
    }

    ALLOWED_HOSTS = []
else:
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

    # Database
    # https://docs.djangoproject.com/en/3.1/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

    ALLOWED_HOSTS = []

export DJANGO_SETTINGS_MODULE=hmmtuf.settings
celery -A hmmtuf worker --loglevel=debug

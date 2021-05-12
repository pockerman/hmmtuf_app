"""
WSGI config for hmmtuf project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import ray

from django.core.wsgi import get_wsgi_application
from compute_engine import INFO


from .config import BASE_DIR
from .config import DEBUG
from .config import USE_CELERY
from .config import ENABLE_SPADE
from .config import SPADE_PATH
from .config import USE_RAY


if USE_RAY:
    import ray

    from .config import RAY_GPUS
    from .config import RAY_PROCESSES

    print("{0} Initializing Ray".format(INFO))
    ray.init(num_cpus=RAY_PROCESSES, num_gpus=RAY_GPUS)


print("{0} Starting HMMtuf WSGI app".format(INFO))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hmmtuf.settings')

application = get_wsgi_application()


print("{0} BASE_DIR: {1}".format(INFO, BASE_DIR))
print("{0} DEBUG: {1}".format(INFO, DEBUG))
print("{0} USE_CELERY: {1}".format(INFO, USE_CELERY))
print("{0} ENABLE_SPADE: {1}".format(INFO, ENABLE_SPADE))
print("{0} SPADE_PATH: {1}".format(INFO, SPADE_PATH))


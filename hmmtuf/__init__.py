# make sure that we start celery_app
# when start our application
from .celery import celery_app as celery_app
from compute_engine import INFO, ENABLE_SPADE
from .settings import BASE_DIR
from .settings import DEBUG
from .settings import USE_CELERY

from .constants import *

print("{0} Starting HMMtuf application".format(INFO))
print("{0} BASE_DIR: {1}".format(INFO, BASE_DIR))
print("{0} DEBUG: {1}".format(INFO, DEBUG))
print("{0} USE_CELERY: {1}".format(INFO, USE_CELERY))
print("{0} ENABLE_SPADE: {1}".format(INFO, ENABLE_SPADE))

# make sure that we start celery_app
# when start our application
from .celery import celery_app as celery_app
from compute_engine import INFO
from .settings import BASE_DIR
from .settings import DEBUG
from .settings import USE_CELERY
#from .settings import process_manager
from .config import NUM_WORKER_PROCESSES
from .config import MAX_QUEUE_JOB_SIZE

print("{0} Starting HMMtuf application".format(INFO))
print("{0} BASE_DIR: {1}".format(INFO, BASE_DIR))
print("{0} DEBUG: {1}".format(INFO, DEBUG))
print("{0} USE_CELERY: {1}".format(INFO, USE_CELERY))

process_manager = None

if USE_CELERY == False:

    print("{0} Initializing ProcessManager".format(INFO))
    from compute_engine.process_worker import ProcessWorkerManager
    #global process_manager
    process_manager = ProcessWorkerManager()
    process_manager.init(num_workers=NUM_WORKER_PROCESSES, max_queue_size=MAX_QUEUE_JOB_SIZE)
else:
    #global process_manager
    process_manager = None
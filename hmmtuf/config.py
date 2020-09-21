from pathlib import Path


#from .celery_settings import BROKER_URL
#from .celery_settings import CELERY_RESULT_BACKEND
#from .celery_settings import CELERY_ACCEPT_CONTENT
#from .celery_settings import CELERY_TASK_SERIALIZER
#from .celery_settings import CELERY_RESULT_SERIALIZER
#from .celery_settings import CELERY_TIMEZONE

REMOTE = False

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

USE_CELERY = False
ENABLE_SPADE = True


if REMOTE:
    BASE_DIR = '/home/a/ag568/hmmtuf_app'

    # Database
    # https://docs.djangoproject.com/en/3.1/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR + '/' + 'db.sqlite3',
        }
    }

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

if DEBUG:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ['127.0.0.1 ', 'localhost',]

SPADE_PATH = "%s/compute_engine/SPADE/" % BASE_DIR

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# TODO: move these to config

# STATIC_URL:
# This is the base URL location
# from which static files will be served, for example on a CDN.
# This is used for the static template variable
# that is accessed in our base template

if DEBUG:
    STATIC_URL = '/static/'
else:
    STATIC_URL = '/deploy_static/'

# This is the absolute path to a directory where Django's "collectstatic" tool will gather
# any static files referenced in our templates.
# Once collected, these can then be uploaded as a group to
# # wherever the files are to be hosted.
STATIC_ROOT = '%s/%s/' % (BASE_DIR, STATIC_URL)
DEV_STATIC_FILES = '%s/%s/' % (BASE_DIR, STATIC_URL)
STATICFILES_DIRS = [DEV_STATIC_FILES]


# path to where to store the region files
REGIONS_FILES_ROOT = '%s/regions/' % BASE_DIR
REGIONS_FILES_URL = '%s/regions/' % BASE_DIR

# path to where to store the HMM files
HMM_FILES_ROOT = '%s/hmm_files/' % BASE_DIR
HMM_FILES_URL = '%s/hmm_files/' % BASE_DIR

# path to where to store the computed Viterbi paths
VITERBI_PATHS_FILES_ROOT = '%s/viterbi_paths/' % BASE_DIR
VITERBI_PATHS_FILES_URL = '%s/viterbi_paths/' % BASE_DIR

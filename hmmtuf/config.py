from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
LOCAL_DEPLOY = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

USE_CELERY = True
ENABLE_SPADE = True
SPADE_PATH = "%s/compute_engine/SPADE/" % BASE_DIR

files_dict = {
  "sequence_files": {

    "files": [{"path": "/home/alex/qi3/hmmtuf/data/",
              "ref_files": ["GCA_000001405.15_GRCh38_no_alt_analysis_set.fna"],
              "no_wga_files": ["m585_verysensitive_trim_sorted.bam"],
              "wga_files": ["m605_verysensitive_trim_sorted.bam"]
     }]
  },
  "sequences_names": {
      "m585_verysensitive_trim_sorted.bam": "M585",
      "m605_verysensitive_trim_sorted.bam": "M605"
    },

    "tdf_files":{
      "m585_verysensitive_trim_sorted.bam": "m585.tdf",
      "m605_verysensitive_trim_sorted.bam": "m605.tdf"
    },
    "igv_tracks":"igv_tracks"
}


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
}

# ALLOWED_HOSTs
# This defines a list of the server’s addresses or
# domain names may be used to connect to the Django instance.
# Any incoming requests with a  Host header that is
# not in this list will raise an exception.
# Django requires that you set this to prevent
# a certain class of security vulnerability.
if DEBUG:
    ALLOWED_HOSTS = []
elif LOCAL_DEPLOY:
    # hosts allowed when in production
    # allow localhost so that we can test
    # deployment version locally
    ALLOWED_HOSTS = ['localhost', ]
else:
    ALLOWED_HOSTS = []


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# STATIC_URL:
# This is the base URL location
# from which static files will be served, for example on a CDN.
# This is used for the static template variable
# that is accessed in the base template

# The STATICFILES_DIRS can contain other directories
# (not necessarily app directories) with static files
# and these static files will be collected into your
# STATIC_ROOT when you run collectstatic.
# These static files will then be served by your
# web server and they will be served from your STATIC_ROOT

if DEBUG:
    STATIC_URL = '/static/'
    DEV_STATIC_FILES = '%s/%s/' % (BASE_DIR, STATIC_URL)
    STATIC_ROOT = ''

    # don't specify it for the moment
    # as we use VITERBI_PATHS_FILES_ROOT
    MEDIA_ROOT = ''
    MEDIA_URL = ''

    # for some reason we need to have the full
    # path to the static files in Debug. Also
    # we don't need to add urlpatterns. This
    # is contrary to what there exists around
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

elif LOCAL_DEPLOY:

    STATIC_URL = '/static/'
    STATIC_ROOT = '%s/%s/' % (BASE_DIR, 'local_deploy_static')
    MEDIA_ROOT = '%s/viterbi_paths/' % BASE_DIR
    MEDIA_URL = '/viterbi_paths/'

    # we need to collect the dev static files
    # and the admin/static
    STATICFILES_DIRS = ['/home/alex/qi3/hmmtuf/static',
                        '/home/alex/.local/lib/python3.6/site-packages/django/contrib/admin/static']

    # path to where to store the region files
    REGIONS_FILES_ROOT = '%s/regions/' % BASE_DIR
    REGIONS_FILES_URL = '%s/regions/' % BASE_DIR

    # path to where to store the HMM files
    HMM_FILES_ROOT = '%s/hmm_files/' % BASE_DIR
    HMM_FILES_URL = '%s/hmm_files/' % BASE_DIR

    # path to where to store the computed Viterbi paths
    VITERBI_PATHS_FILES_ROOT = 'http://localhost/viterbi_paths/'
    VITERBI_PATHS_FILES_URL = 'http://localhost/viterbi_paths/'

else:

    # these fields depend on where/how we actually
    # want to deploy

    STATIC_URL = ''

    # This is the absolute path to a directory
    # where Django's "collectstatic" tool will gather
    # any static files referenced in our templates.
    # This is not where the static files are already at.
    # Once collected, these can then be uploaded as a group to
    # # wherever the files are to be hosted.
    STATIC_ROOT = '' #'%s/%s/' % (BASE_DIR, STATIC_URL)
    STATICFILES_DIRS = []

    MEDIA_ROOT = ''
    MEDIA_URL = ''

    # path to where to store the region files
    REGIONS_FILES_ROOT = ''
    REGIONS_FILES_URL = ''

    # path to where to store the HMM files
    HMM_FILES_ROOT = ''
    HMM_FILES_URL = ''

    # path to where to store the computed Viterbi paths
    VITERBI_PATHS_FILES_ROOT = ''
    VITERBI_PATHS_FILES_URL = ''

if DEBUG is False and LOCAL_DEPLOY is False:
    if STATIC_URL == '' or STATIC_ROOT == '':
        raise Exception("Improperly configured for production")



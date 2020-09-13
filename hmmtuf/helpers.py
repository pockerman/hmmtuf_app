from .settings import BASE_DIR
from .settings import VITERBI_PATHS_FILES_ROOT
from .constants import VITERBI_PATH_FILENAME
from compute_engine.utils import read_json


def get_configuration():
    return read_json(filename=make_configuration_path())


def make_configuration_path():
    return "%s/config.json" % BASE_DIR


def make_viterbi_path(task_id):
    return VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/" + VITERBI_PATH_FILENAME
from .settings import VITERBI_PATHS_FILES_ROOT
from .settings import HMM_FILES_ROOT
from .constants import VITERBI_PATH_FILENAME
from .constants import TUF_DEL_TUF_PATH_FILENAME
from .constants import VITERBI_SEQUENCE_FILENAME
from .constants import VITERBI_SEQUENCE_COMPARISON_FILENAME
from .config import files_dict
from .config import VITERBI_SEQ_FILES_ROOT
from .config import VITERBI_SEQ_COMPARISON_FILES_ROOT


def get_configuration():
    return files_dict


def make_hmm_file_path(hmm_name):
    return HMM_FILES_ROOT + hmm_name


def make_viterbi_path_filename(task_id, extra_path=None):

    if extra_path is None:
        return VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/" + VITERBI_PATH_FILENAME
    else:
        return VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/" + extra_path + "/" + VITERBI_PATH_FILENAME


def make_tuf_del_tuf_path_filename(task_id, extra_path=None):

    if extra_path is None:
        return VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/" + TUF_DEL_TUF_PATH_FILENAME
    else:
        return VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/" + extra_path + "/" + TUF_DEL_TUF_PATH_FILENAME


def make_viterbi_sequence_path_filename(task_id, extra_path=None):

    if extra_path is None:
        return VITERBI_SEQ_FILES_ROOT + task_id.replace('-', '_') + "/" + VITERBI_SEQUENCE_FILENAME
    else:
        return VITERBI_SEQ_FILES_ROOT + task_id.replace('-', '_') + "/" + extra_path + "/" + VITERBI_SEQUENCE_FILENAME


def make_viterbi_sequence_path(task_id, extra_path=None):

    if extra_path is None:
        return VITERBI_SEQ_FILES_ROOT + task_id.replace('-', '_') + "/"
    else:
        return VITERBI_SEQ_FILES_ROOT + task_id.replace('-', '_') + "/" + extra_path + "/"


def make_viterbi_sequence_comparison_path_filename(task_id, extra_path=None):
    if extra_path is None:
        return VITERBI_SEQ_COMPARISON_FILES_ROOT + task_id.replace('-', '_') + \
               "/" + VITERBI_SEQUENCE_COMPARISON_FILENAME
    else:
        return VITERBI_SEQ_COMPARISON_FILES_ROOT + task_id.replace('-', '_') + \
               "/" + extra_path + "/" + VITERBI_SEQUENCE_COMPARISON_FILENAME


def make_viterbi_sequence_comparison_path(task_id, extra_path=None):

    if extra_path is None:
        return VITERBI_SEQ_COMPARISON_FILES_ROOT + task_id.replace('-', '_') + "/"
    else:
        return VITERBI_SEQ_COMPARISON_FILES_ROOT + task_id.replace('-', '_') + "/" + extra_path + "/"


def make_viterbi_path(task_id):
    return VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/"


def make_ref_sequence_path_filename(filename):
    configuration = get_configuration()
    files = configuration["sequence_files"]["files"]

    for idx in range(len(files)):
        map = files[idx]
        ref_files = map["ref_files"]

        if filename in ref_files:
            return map["path"] + filename

    raise ValueError("Filename {0} not "
                     "in configuration given".format(filename))


def make_bed_path(task_id, bed_name):
    return VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/" + bed_name

import json
import time
from functools import wraps
from enum import Enum
import logging
import time

INFO = "INFO:"
ERROR = "ERROR:"
DEBUG = "DEBUG:"
WARNING = "WARNING:"
OK = True
DUMMY_ID = -1
DEFAULT_ERROR_EXPLANATION = "No error occurred"
INVALID_STR = 'INVALID'


def timefn(fn):
    @wraps(fn)
    def measure(*args, **kwargs):
        time_start = time.perf_counter()
        result = fn(*args, **kwargs)
        time_end = time.perf_counter()
        print("{0} Done. Execution time"
              " {1} secs".format(INFO, time_end - time_start))
        return result

    return measure


def read_json(filename):

    """
        Read the json configuration file and
        return a map with the config entries
    """
    with open(filename) as json_file:
        json_input = json.load(json_file)
        return json_input


def extract_file_names(configuration):

    reference_files_names = []
    ref_files = configuration["sequence_files"]["reference_files"]

    for i in range(len(ref_files)):
        files = configuration["sequence_files"]["reference_files"][i]

        for f in files:
            reference_files_names.extend(files[f])

    wga_files_names = []
    wga_files = configuration["sequence_files"]["wga_files"]

    for i in range(len(wga_files)):
        files = configuration["sequence_files"]["wga_files"][i]

        for f in files:
            wga_files_names.extend(files[f])

    nwga_files_names = []
    nwga_files = configuration["sequence_files"]["no_wga_files"]

    for i in range(len(nwga_files)):
        files = configuration["sequence_files"]["no_wga_files"][i]

        for f in files:
            nwga_files_names.extend(files[f])

    return reference_files_names, wga_files_names, nwga_files_names


def extract_path(configuration, ref_file):
    reference_files_names = []
    ref_files = configuration["sequence_files"]["reference_files"]

    for i in range(len(ref_files)):
        files = configuration["sequence_files"]["reference_files"][i]

        for f in files:
            if ref_file in files[f]:
                return f

    return None




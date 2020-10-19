import json
from functools import wraps
import time

from compute_engine.src.constants import INFO

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
    wga_files_names = []
    nwga_files_names = []
    files = configuration["sequence_files"]["files"]

    for idx in range(len(files)):
        map = files[idx]
        ref_files = map["ref_files"]
        reference_files_names.extend(ref_files)

        wga_files = map["wga_files"]
        wga_files_names.extend(wga_files)

        nwga_files = map["no_wga_files"]
        nwga_files_names.extend(nwga_files)

    return reference_files_names, wga_files_names, nwga_files_names


def extract_path(configuration, ref_file):
    files = configuration["sequence_files"]["files"]

    for idx in range(len(files)):
        map = files[idx]
        ref_files = map["ref_files"]

        if ref_file in ref_files:
            return map["path"]
    return None


def get_sequence_name(configuration, seq):
    return configuration["sequences_names"][seq]


def get_tdf_file(configuration, seq):
    return configuration["tdf_files"][seq]


def read_sequence_bed_file(filename, delim='\t'):

    sequence = ''
    with open(filename, 'r') as f:
        for line in f:
            line = line.split(delim)
            sequence += line[-1].strip('\n')

    return sequence







import json
import time
from functools import wraps

INFO = "INFO:"
ERROR = "ERROR:"


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

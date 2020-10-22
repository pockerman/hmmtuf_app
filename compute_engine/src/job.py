from enum import Enum

from compute_engine.src.constants import DEFAULT_ERROR_EXPLANATION


class JobResultEnum(Enum):
    PENDING = 0
    FAILURE = 1
    SUCCESS = 2
    CREATED = 4


class JobType(Enum):
    VITERBI = 0
    EXTRACT_REGION = 1
    MULTI_VITERBI = 2
    GROUP_VITERBI = 3
    VITERBI_SEQUENCE_COMPARE = 4
    VITERBI_GROUP_ALL = 5


class Job(object):
    def __init__(self, idx, input, worker):
        self._idx = idx

        self._status = JobResultEnum.CREATED.name
        self._error_msg = DEFAULT_ERROR_EXPLANATION
        self._input = input
        self._worker = worker

    def execute(self):

        self._status = JobResultEnum.PENDING.name

        try:
            self._worker(self._input)
            self._status = JobResultEnum.SUCCESS.name
        except Exception as e:
            self._status = JobResultEnum.FAILURE.name
            self._error_msg = str(e)

        finally:
            self.save()

    def save(self):
        pass

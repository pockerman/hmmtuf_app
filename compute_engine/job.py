from enum import Enum

from .constants import DEFAULT_ERROR_EXPLANATION


class JobResultEnum(Enum):
    PENDING = 0
    FAILURE = 1
    SUCCESS = 2


class JobType(Enum):
    VITERBI = 0
    EXTRACT_REGION = 1
    MULTI_VITERBI = 2
    GROUP_VITERBI = 3
    VITERBI_SEQUENCE_COMPARE = 4
    SCHEDULE_VITERBI_GROUP_ALL_COMPUTATION = 5


class Job(object):
    def __init__(self, idx, input, worker, model=None):
        self._idx = idx
        self._started = False
        self._ended = False
        self._result = ""
        self._error_msg = DEFAULT_ERROR_EXPLANATION
        self._input = input
        self._worker = worker
        self._model = model

    def execute(self):

        self._started = JobResultEnum.PENDING

        if self._model is not None:
            self._model.result = JobResultEnum.PENDING
            self._model.error_explanation = DEFAULT_ERROR_EXPLANATION
            self.save()
        try:
            self._worker(self._input)
            self._ended = True
            self._result = JobResultEnum.SUCCESS
        except Exception as e:
            self._result = JobResultEnum.FAILURE
            self._error_msg = str(e)

            if self._model is not None:
                self._model.result = JobResultEnum.FAILURE
                self._model.error_explanation = str(e)
        finally:
            self.save()

    def save(self):
        if self._model is not None:
            print("Saving the model")
            self._model.save()
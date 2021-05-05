from enum import Enum

from compute_engine.src.constants import DEFAULT_ERROR_EXPLANATION

class JobResultEnum(Enum):
    """
    Job result enumeration
    """
    PENDING = 0
    FAILURE = 1
    SUCCESS = 2
    CREATED = 4

class JobType(Enum):
    """
    Job type enumeration
    """
    VITERBI = 0
    EXTRACT_REGION = 1
    GROUP_VITERBI = 3
    VITERBI_SEQUENCE_COMPARE = 4
    VITERBI_GROUP_ALL = 5
    KMER = 6

class BackendType(Enum):
    """
    Backend type enumeration
    """
    SKLEARN = 0
    PYTORCH = 1

class ClassifierType(Enum):
    """
    Classifier type enumeration
    """
    SKLEARN_LOGISTIC_REGRESSOR = 0
    PYTORCH_LOGISTIC_REGRESSOR = 1


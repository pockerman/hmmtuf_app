from django.db import models

from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine import DEFAULT_ERROR_EXPLANATION


class ComputationModel(models.Model):
    """
    Abstract base class for DB computation
    """

    RESULT_OPTIONS = ((JobResultEnum.PENDING.name, JobResultEnum.PENDING.name),
                      (JobResultEnum.SUCCESS.name, JobResultEnum.SUCCESS.name),
                      (JobResultEnum.FAILURE.name, JobResultEnum.FAILURE.name),
                      )

    # the task id of the computation
    task_id = models.CharField(max_length=300, primary_key=True)
    result = models.CharField(max_length=50, choices=RESULT_OPTIONS)
    error_explanation = models.CharField(max_length=500, default=DEFAULT_ERROR_EXPLANATION)
    computation_type = models.CharField(max_length=100)

    class Meta:
        abstract = True
from django.db import models
from webapp_utils.model_utils import ComputationModel
# Create your models here.

from hmmtuf.config import BED_COMPARE_FILES_ROOT


def upload_bed_file(instance, filename: str):
    return BED_COMPARE_FILES_ROOT + filename


class BedComparisonModel(ComputationModel):

    # the viterbi path
    viterbi_filename = models.CharField(max_length=1000)

    # the bed file
    bed_filename = models.CharField(max_length=1000)

    # the result file written
    result_filename = models.CharField(max_length=1000)

    class Meta(ComputationModel.Meta):
        db_table = 'bed_comparison_computation'



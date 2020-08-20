
from enum import Enum
from django.db import models
from json import JSONEncoder

# Create your models here.


from .tasks import compute_viterbi_path_task

DEFAULT_ERROR_EXPLANATION = "No error occurred"

class ComputationResultEnum(Enum):
    PENDING = 0
    FAILURE = 1
    SUCCESS = 2


class ComputationType(Enum):
    VITERBI = 0


class ComputationEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Computation(models.Model):

    RESULT_OPTIONS = ((ComputationResultEnum.PENDING.name, ComputationResultEnum.PENDING.name),
                      (ComputationResultEnum.SUCCESS.name, ComputationResultEnum.SUCCESS.name),
                      (ComputationResultEnum.FAILURE.name, ComputationResultEnum.FAILURE.name),
                      )

    # the task id of the computation
    task_id = models.CharField(max_length=300, primary_key=True)
    result = models.CharField(max_length=50, choices=RESULT_OPTIONS)
    error_explanation = models.CharField(max_length=500, default=DEFAULT_ERROR_EXPLANATION)
    computation_type = models.CharField(max_length=100)

    class Meta:
        abstract = True


class ViterbiComputation(Computation):

    # the resulting viterbi path file
    file_viterbi_path = models.FileField()

    # the region name used for the computation
    region_filename = models.CharField(max_length=500)

    # the hmm model used for the computation
    hmm_filename = models.CharField(max_length=500)

    # chromosome
    chromosome = models.CharField(max_length=10)

    # sequence size
    seq_size = models.IntegerField()

    class Meta(Computation.Meta):
        db_table = 'viterbi_computation'

    @staticmethod
    def build_from_map(map, save):
        computation = ViterbiComputation()
        computation.task_id = map["task_id"]
        computation.result = map["result"]
        computation.error_explanation = map["error_explanation"]
        computation.computation_type = map["computation_type"]
        computation.file_viterbi_path = map["viterbi_path_filename"]
        computation.region_filename = map["region_filename"]
        computation.hmm_filename = map["hmm_filename"]
        computation.chromosome = map["chromosome"]
        computation.seq_size = map["seq_size"]

        if save:
            computation.save()
        return computation

    @staticmethod
    def compute(data):

        hmm_name = data['hmm_name']
        chromosome = data['chromosome']
        window_type = str(data['window_type'])
        viterbi_path_filename = data['viterbi_path_filename']
        region_filename = data['region_filename']
        hmm_filename = data['hmm_filename']
        sequence_size = data['sequence_size']
        n_sequences = data['n_sequences']

        # schedule the computation
        return compute_viterbi_path_task.delay(hmm_name=hmm_name,
                                                chromosome=chromosome, window_type=window_type,
                                                viterbi_path_filename=viterbi_path_filename,
                                                region_filename=region_filename,
                                                hmm_filename=hmm_filename,
                                                sequence_size=sequence_size, n_sequences=n_sequences,
                                                path_img=data['path_img'])












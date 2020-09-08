
from enum import Enum
from json import JSONEncoder
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


# Create your models here.

from compute_engine.utils import DEFAULT_ERROR_EXPLANATION, INFO
from compute_engine.windows import WindowType
from .tasks import compute_viterbi_path_task


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

    # the reference sequence filename
    ref_seq_filename = models.CharField(max_length=1000)

    # the reference sequence filename
    wga_seq_filename = models.CharField(max_length=1000)

    # the reference sequence filename
    no_wag_seq_filename = models.CharField(max_length=1000)

    # the hmm model used for the computation
    hmm_filename = models.CharField(max_length=500)

    # chromosome
    chromosome = models.CharField(max_length=10)

    # sequence size
    seq_size = models.IntegerField()

    # number of gaps
    number_of_gaps = models.IntegerField()

    # the hmm model image
    hmm_path_img = models.FileField(null=True)

    # how many sequences used for the viterbi calculation
    extracted_sequences = models.IntegerField(default=1)

    # number of mixed windows used in the computation
    n_mixed_windows = models.IntegerField(default=0)

    # type of the window
    window_type = models.CharField(max_length=20, default=WindowType.BOTH.name)


    class Meta(Computation.Meta):
        db_table = 'viterbi_computation'

    @staticmethod
    def build_from_map(map, save):

        print("{0} build_from_map computation: {1}".format(INFO, map["task_id"]))


        try:
            computation = ViterbiComputation.objects.get(task_id=map["task_id"])
            return computation
        except ObjectDoesNotExist:

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
                computation.ref_seq_filename = map["ref_seq_file"]
                computation.wga_seq_filename = map["wga_seq_file"]
                computation.no_wag_seq_filename = map["no_wag_seq_file"]
                computation.number_of_gaps = map["number_of_gaps"]
                computation.hmm_path_img = map["hmm_path_img"]
                computation.extracted_sequences = map["extracted_sequences"]
                computation.n_mixed_windows = map["n_mixed_windows"]
                computation.window_type = map["window_type"]

                if save:
                    computation.save()
                    print("{0} saved computation: {1}".format(INFO, map["task_id"]))
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
        ref_seq_file = data["ref_seq_file"]
        wga_seq_file = data["wga_seq_file"]
        no_wag_seq_file = data["no_wag_seq_file"]

        # schedule the computation
        return compute_viterbi_path_task.delay(hmm_name=hmm_name,
                                                chromosome=chromosome, window_type=window_type,
                                                viterbi_path_filename=viterbi_path_filename,
                                                region_filename=region_filename,
                                                hmm_filename=hmm_filename,
                                                sequence_size=sequence_size, n_sequences=n_sequences,
                                                path_img=data['path_img'],
                                                viterbi_path_files_root=data['viterbi_path_files_root'],
                                                ref_seq_file=ref_seq_file,
                                                no_wag_seq_file=no_wag_seq_file,
                                                wga_seq_file=wga_seq_file)












from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from compute_engine import INFO, INVALID_STR
from compute_engine.job import JobType, JobResultEnum
from compute_engine.windows import WindowType
from hmmtuf import INVALID_ITEM
from hmmtuf.settings import USE_CELERY
from hmmtuf_home.models import Computation, RegionGroupTipModel

from .tasks import compute_viterbi_path_task
from .tasks import compute_mutliple_viterbi_path_task
from .tasks import compute_group_viterbi_path_task


class GroupViterbiComputation(Computation):
    """
    Represents a group Viterbi computation task in the DB
    All fields are NULL by default as the computation may fail
    before computing the relevant field. Instances of this class
    are created by the tasks.compute_viterbi_path_task
    which tries to fill in as many fields as possible. Upon successful
    completion of the task all fields should have valid values
    """

    # the tip used for the computation
    group_tip = models.CharField(max_length=100, null=True)

    # the hmm model used for the computation
    hmm_filename = models.CharField(max_length=500, null=True)

    # the hmm model image
    hmm_path_img = models.FileField(null=True)

    @staticmethod
    def build_from_map(map_data, save):

        try:
            computation = GroupViterbiComputation.objects.get(task_id=map_data["task_id"])
            return computation
        except ObjectDoesNotExist:

            computation = ViterbiComputation()
            computation.task_id = map_data["task_id"]
            computation.result = map_data["result"]
            computation.error_explanation = map_data["error_explanation"]
            computation.computation_type = map_data["computation_type"]
            computation.hmm_filename = map_data["hmm_filename"]
            computation.hmm_path_img = map_data["hmm_path_img"]
            computation.window_type = map_data["window_type"]
            computation.group_tip = map_data["group_tip"]

            if save:
                computation.save()
                print("{0} saved computation: {1}".format(INFO, map_data["task_id"]))
            return computation

    @staticmethod
    def compute(data):

        hmm_name = data['hmm_name']
        window_type = 'BOTH'

        if USE_CELERY:

            # schedule the computation
            task = compute_group_viterbi_path_task.delay(hmm_name=hmm_name,
                                                         window_type=window_type,
                                                         group_tip=data["group_tip"])
            return task.id
        else:

            import uuid
            from .tasks import compute_group_viterbi_path
            task_id = str(uuid.uuid4())
            compute_group_viterbi_path(task_id=task_id,
                                       hmm_name=hmm_name,
                                       window_type=window_type,
                                       group_tip=data["group_tip"])
            return task_id

    @staticmethod
    def get_invalid_map(task, result):
        data_map = dict()

        data_map["task_id"] = task.id
        data_map["result"] = JobResultEnum.FAILURE.name
        data_map["error_explanation"] = str(result)
        data_map["computation_type"] = JobType.GROUP_VITERBI.name
        data_map["hmm_filename"] = result["hmm_filename"]
        data_map["hmm_path_img"] = INVALID_ITEM
        data_map["window_type"] = INVALID_STR
        data_map["group_tip"] = result["group_tip"]
        return data_map


class ViterbiComputation(Computation):
    """
    Represents a Viterbi computation task in the DB
    All fields are NULL by default as the computation may fail
    before computing the relevant field. Instances of this class
    are created by the tasks.compute_viterbi_path_task
    which tries to fill in as many fields as possible. Upon successful
    completion of the task all fields should have valid values
    """

    # the resulting viterbi path file
    file_viterbi_path = models.FileField(null=True)

    # the region name used for the computation
    region_filename = models.CharField(max_length=500, null=True)

    # the reference sequence filename
    ref_seq_filename = models.CharField(max_length=1000, null=True)

    # the reference sequence filename
    wga_seq_filename = models.CharField(max_length=1000, null=True)

    # the reference sequence filename
    no_wag_seq_filename = models.CharField(max_length=1000, null=True)

    # the hmm model used for the computation
    hmm_filename = models.CharField(max_length=500, null=True)

    # chromosome
    chromosome = models.CharField(max_length=10, null=True)

    # sequence size
    seq_size = models.IntegerField(null=True)

    # number of gaps
    number_of_gaps = models.IntegerField(null=True)

    # the hmm model image
    hmm_path_img = models.FileField(null=True)

    # how many sequences used for the viterbi calculation
    extracted_sequences = models.IntegerField(default=1, null=True)

    # number of mixed windows used in the computation
    n_mixed_windows = models.IntegerField(default=0, null=True)

    # type of the window
    window_type = models.CharField(max_length=20, default=WindowType.BOTH.name, null=True)

    class Meta(Computation.Meta):
        db_table = 'viterbi_computation'

    @staticmethod
    def build_from_map(map, save):

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
            computation.ref_seq_filename = map["ref_seq_file"]
            computation.wga_seq_filename = map["wga_seq_file"]
            computation.no_wag_seq_filename = map["no_wag_seq_file"]
            computation.hmm_filename = map["hmm_filename"]
            computation.chromosome = map["chromosome"]
            computation.seq_size = map["seq_size"]
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
        region_filename = data['region_filename']
        hmm_filename = data['hmm_filename']
        ref_seq_file = data["ref_seq_file"]
        wga_seq_file = data["wga_seq_file"]
        no_wga_seq_file = data["no_wag_seq_file"]

        if USE_CELERY:

            # schedule the computation
            task = compute_viterbi_path_task.delay(hmm_name=hmm_name,
                                                   chromosome=chromosome,
                                                   chromosome_index=data["chromosome_index"],
                                                   window_type=window_type,
                                                   region_filename=region_filename,
                                                   hmm_filename=hmm_filename,
                                                   sequence_size=None,
                                                   n_sequences=1,
                                                   ref_seq_file=ref_seq_file,
                                                   no_wga_seq_file=no_wga_seq_file,
                                                   wga_seq_file=wga_seq_file,
                                                   remove_dirs=data["remove_dirs"],
                                                   use_spade=data["use_spade"])
            return task.id
        else:

            import uuid
            from .tasks import compute_viterbi_path
            task_id = str(uuid.uuid4())
            compute_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                 chromosome=chromosome, chromosome_index=data["chromosome_index"],
                                 window_type=window_type, region_filename=region_filename,
                                 hmm_filename=hmm_filename, sequence_size=None, n_sequences=1,
                                 ref_seq_file=ref_seq_file, no_wga_seq_file=no_wga_seq_file,
                                 wga_seq_file=wga_seq_file, remove_dirs=data["remove_dirs"],
                                 use_spade=data["use_spade"])
            return task_id

    @staticmethod
    def get_invalid_map(task, result):
        data_map = dict()

        data_map["task_id"] = task.id
        data_map["result"] = JobResultEnum.FAILURE.name
        data_map["error_explanation"] = str(result)
        data_map["computation_type"] = JobType.VITERBI.name
        data_map["viterbi_path_filename"] = result["viterbi_path_filename"]
        data_map["region_filename"] = result["region_filename"]
        data_map["hmm_filename"] = result["hmm_filename"]
        data_map["chromosome"] = result["chromosome"]
        data_map["seq_size"] = result["seq_size"]
        data_map["ref_seq_file"] = INVALID_STR
        data_map["wga_seq_file"] = INVALID_STR
        data_map["no_wag_seq_file"] = INVALID_STR
        data_map["number_of_gaps"] = 0
        data_map["hmm_path_img"] = INVALID_ITEM
        data_map["extracted_sequences"] = 0
        data_map["n_mixed_windows"] = 0
        data_map["window_type"] = INVALID_STR
        return data_map


class MultiViterbiComputation(Computation):
    """
    Represents a multi-Viterbi computation task in the DB
    All fields are NULL by default as the computation may fail
    before computing the relevant field. Instances of this class
    are created by the tasks.compute_mutliple_viterbi_path_task
    which tries to fill in as many fields as possible. Upon successful
    completion of the task all fields should have valid values
    """

    # the resulting viterbi path file
    file_viterbi_path = models.FileField(null=True)

    # chromosome
    chromosome = models.CharField(max_length=10, null=True)

    # the hmm model used for the computation
    hmm_filename = models.CharField(max_length=500, null=True)

    # the reference sequence filename
    ref_seq_filename = models.CharField(max_length=1000, null=True)

    # the reference sequence filename
    wga_seq_filename = models.CharField(max_length=1000, null=True)

    # the reference sequence filename
    no_wag_seq_filename = models.CharField(max_length=1000, null=True)

    # number of regions used
    n_regions = models.IntegerField(null=True)

    # the hmm model image
    hmm_path_img = models.FileField(null=True)

    class Meta(Computation.Meta):
        db_table = 'multi_viterbi_computation'

    @staticmethod
    def build_from_map(map, save):

        try:
            computation = MultiViterbiComputation.objects.get(task_id=map["task_id"])
            return computation
        except ObjectDoesNotExist:

            computation = MultiViterbiComputation()
            computation.task_id = map["task_id"]
            computation.result = map["result"]
            computation.error_explanation = map["error_explanation"]
            computation.computation_type = map["computation_type"]
            computation.hmm_filename = map["hmm_filename"]
            computation.ref_seq_filename = map["ref_seq_filename"]
            computation.wga_seq_filename = map["wga_seq_filename"]
            computation.no_wag_seq_filename = map["no_wga_seq_filename"]
            computation.chromosome = map["chromosome"]
            computation.n_regions = map["n_regions"]
            computation.file_viterbi_path = map["file_viterbi_path"]
            computation.hmm_path_img = map["hmm_path_img"]

            if save:
                computation.save()
                print("{0} saved computation: {1}".format(INFO, map["task_id"]))
            return computation

    @staticmethod
    def compute(data):

        hmm_name = data['hmm_name']
        chromosome = data['chromosome']
        window_type = 'BOTH'
        viterbi_path_filename = data['viterbi_path_filename']
        ref_seq_file = data["ref_seq_filename"]
        wga_seq_file = data["wga_seq_filename"]
        no_wag_seq_file = data["no_wga_seq_filename"]

        # schedule the computation
        task = compute_mutliple_viterbi_path_task.delay(hmm_name=hmm_name,
                                                        chromosome=chromosome,
                                                        window_type=window_type,
                                                        viterbi_path_filename=viterbi_path_filename,
                                                        group_tip=data['group_tip'],
                                                        ref_seq_file=ref_seq_file,
                                                        no_wga_seq_file=no_wag_seq_file,
                                                        wga_seq_file=wga_seq_file)

        return task.id

    @staticmethod
    def get_invalid_map(task, result):

        data_map = dict()
        data_map["task_id"] = task.id
        data_map["result"] = JobResultEnum.FAILURE.name
        data_map["error_explanation"] = str(result)
        data_map["computation_type"] = JobType.MULTI_VITERBI.name
        data_map["file_viterbi_path"] = result["file_viterbi_path"]
        data_map["hmm_filename"] = result["hmm_filename"]
        data_map["chromosome"] = result["chromosome"]
        data_map["ref_seq_filename"] = result["ref_seq_filename"]
        data_map["wga_seq_filename"] = result["wga_seq_filename"]
        data_map["no_wag_seq_filename"] = result["no_wga_seq_filename"]
        data_map["window_type"] = result["window_type"]
        data_map["n_regions"] = result["n_regions"]
        data_map["hmm_path_img"] = result["hmm_path_img"]
        return data_map

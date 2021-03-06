from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from compute_engine import INFO, INVALID_STR
from compute_engine.src.enumeration_types import JobType, JobResultEnum
from compute_engine.src.windows import WindowType
from hmmtuf import INVALID_ITEM
from hmmtuf.settings import USE_CELERY
from hmmtuf_home.models import ComputationModel
from hmmtuf_home.models import RepeatsModel

from .tasks import compute_viterbi_path_task
from .tasks import compute_group_viterbi_path_task
from .tasks import compute_group_viterbi_path_all_task


class GroupViterbiComputationModel(ComputationModel):
    """
    Represents a group Viterbi computation task in the DB
    All fields are NULL by default as the computation may fail
    before computing the relevant field. Instances of this class
    are created by the tasks.compute_viterbi_path_task
    which tries to fill in as many fields as possible. Upon successful
    completion of the task all fields should have valid values
    """
    
# TODO: Add here the job type

    # the tip used for the computation
    group_tip = models.CharField(max_length=100, null=True)

    # the hmm model used for the computation
    hmm_filename = models.CharField(max_length=500, null=True)

    # the hmm model image
    hmm_path_img = models.FileField(null=True)

    # the reference sequence filename
    ref_seq_filename = models.CharField(max_length=1000, null=True)

    # the reference sequence filename
    wga_seq_filename = models.CharField(max_length=1000, null=True)

    # the reference sequence filename
    no_wag_seq_filename = models.CharField(max_length=1000, null=True)

    # number of regions
    number_regions = models.IntegerField(null=True)

    # the chromosome of the group
    chromosome = models.CharField(max_length=100, null=True)

    # start index of the first region in the group
    start_region_idx = models.IntegerField(null=True)

    # end index of the first region in the group
    end_region_idx = models.IntegerField(null=True)

    class Meta(ComputationModel.Meta):
        db_table = 'group_viterbi_computation'

    @staticmethod
    def get_as_map(model):
        return {"task_id": model.task_id,
                "result": model.result,
                "error_explanation": model.error_explanation,
                "computation_type": model.computation_type,
                "group_tip": model.group_tip,
                "hmm_filename": model.hmm_filename,
                "hmm_path_img": model.hmm_path_img,
                "ref_seq_filename": model.ref_seq_filename,
                "wga_seq_filename": model.wga_seq_filename,
                "no_wag_seq_filename": model.no_wag_seq_filename,
                "scheduler_id": model.scheduler_id,
                "number_regions": model.number_regions,
                "chromosome": model.chromosome,
                "start_region_idx": model.start_region_idx,
                "end_region_idx": model.end_region_idx}

    @staticmethod
    def build_from_map(map_data, save):

        try:
            computation = GroupViterbiComputationModel.objects.get(task_id=map_data["task_id"])
            return computation
        except ObjectDoesNotExist:

            computation = ViterbiComputationModel()
            computation.task_id = map_data["task_id"]
            computation.result = map_data["result"]
            computation.error_explanation = map_data["error_explanation"]
            computation.computation_type = map_data["computation_type"]
            computation.hmm_filename = map_data["hmm_filename"]
            computation.hmm_path_img = map_data["hmm_path_img"]
            computation.window_type = map_data["window_type"]
            computation.group_tip = map_data["group_tip"]
            computation.ref_seq_filename = map_data["ref_seq_file"]
            computation.wga_seq_filename = map_data["wga_seq_file"]
            computation.no_wag_seq_filename = map_data["no_wag_seq_file"]
            computation.scheduler_id = map_data["scheduler_id"]
            computation.number_regions = map_data["number_regions"]
            computation.chromosome = map_data["chromosome"]
            computation.start_region_idx = map_data["start_region_idx"]
            computation.end_region_idx = map_data["end_region_idx"]

            if save:
                computation.save()
                print("{0} saved computation: {1}".format(INFO, map_data["task_id"]))
            return computation

    @staticmethod
    def compute(data):

        hmm_name = data['hmm_name']
        window_type = 'BOTH'

        if USE_CELERY:

            if data["group_tip"] == 'all':
                task = compute_group_viterbi_path_all_task.delay(hmm_name=hmm_name,
                                                                 window_type=window_type,
                                                                 remove_dirs=data["remove_dirs"],
                                                                 use_spade=data["use_spade"],
                                                                 sequence_group=data['sequence_group'])
            else:
                # schedule the computation
                task = compute_group_viterbi_path_task.delay(hmm_name=hmm_name,
                                                             window_type=window_type,
                                                             group_tip=data["group_tip"],
                                                             remove_dirs=data["remove_dirs"],
                                                             use_spade=data["use_spade"],
                                                             sequence_group=data["sequence_group"])
            return task
        else:

            import uuid

            if data["group_tip"] == 'all':

                from .tasks import compute_group_viterbi_path_all
                task_id = str(uuid.uuid4())
                compute_group_viterbi_path_all(task_id=task_id,
                                               hmm_name=hmm_name,
                                               window_type=window_type,
                                               remove_dirs=data["remove_dirs"],
                                               use_spade=data["use_spade"],
                                               sequence_group=data["sequence_group"])
                return task_id

            else:
                from .tasks import compute_group_viterbi_path
                task_id = str(uuid.uuid4())
                compute_group_viterbi_path(task_id=task_id,
                                           hmm_name=hmm_name,
                                           window_type=window_type,
                                           group_tip=data["group_tip"],
                                           remove_dirs=data["remove_dirs"],
                                           use_spade=data["use_spade"],
                                           scheduler_id=data["scheduler_id"],
                                           sequence_group=data["sequence_group"])
                return task_id

    @staticmethod
    def get_invalid_map(task, result):
        data_map = dict()

        data_map["task_id"] = task.id
        data_map["result"] = JobResultEnum.FAILURE.name
        data_map["error_explanation"] = str(result)
        data_map["computation_type"] = JobType.GROUP_VITERBI.name
        data_map["hmm_filename"] = result["hmm_filename"]
        data_map["hmm_path_img"] = result["hmm_path_img"]
        data_map["window_type"] = result["window_type"]
        data_map["group_tip"] = result["group_tip"]
        data_map["ref_seq_file"] = result["ref_seq_file"]
        data_map["wga_seq_file"] = result["wga_seq_file"]
        data_map["no_wag_seq_file"] = result["no_wag_seq_file"]
        data_map["scheduler_id"] = result["scheduler_id"]
        data_map["number_regions"] = result["number_regions"]
        data_map["sequence_group"] = result["sequence_group"]
        data_map["chromosome"] = result["chromosome"]
        data_map["start_region_idx"] = result["start_region_idx"]
        data_map["end_region_idx"] = result["end_region_idx"]
        return data_map


class ViterbiComputationModel(ComputationModel):
    """
    DB model for a Viterbi computation task
    All fields are NULL by default as the computation may fail
    before computing the relevant field. Instances of this class
    are created by the tasks.compute_viterbi_path_task
    which tries to fill in as many fields as possible. Upon successful
    completion of the task all fields should have valid values
    """

    # the type of the computation
    JOB_TYPE = JobType.VITERBI.name

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

    # start index of the region
    start_region_idx = models.IntegerField(null=True)

    # end index of the region
    end_region_idx = models.IntegerField(null=True)

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

    class Meta(ComputationModel.Meta):
        db_table = 'viterbi_computation'

    @staticmethod
    def get_as_map(model):
        return {"task_id": model.task_id, "result": model.result,
                "error_explanation": model.error_explanation,
                "computation_type": model.computation_type,
                "viterbi_path_filename": model.file_viterbi_path.name,
                "region_filename": model.region_filename,
                "ref_seq_filename": model.ref_seq_filename,
                "wga_seq_filename": model.wga_seq_filename,
                "no_wag_seq_filename": model.no_wag_seq_filename,
                "hmm_filename": model.hmm_filename,
                "chromosome": model.chromosome,
                "seq_size": model.seq_size,
                "number_of_gaps": model.number_of_gaps,
                "hmm_path_img": model.hmm_path_img,
                "extracted_sequences": model.extracted_sequences,
                "n_mixed_windows": model.n_mixed_windows,
                "window_type": model.window_type,
                "scheduler_id": model.scheduler_id,
                "start_region_idx": model.start_region_idx,
                "end_region_idx": model.end_region_idx}

    @staticmethod
    def build_from_data(task_id, result, error_explanation,
                        file_viterbi_path, region_filename, ref_seq_filename,
                        wga_seq_filename, no_wag_seq_filename, hmm_filename,
                        chromosome, start_region_idx, end_region_idx,
                        seq_size, number_of_gaps, hmm_path_img,
                        extracted_sequences, n_mixed_windows, window_type, scheduler_id,  save):

        map_data = dict()
        map_data["task_id"] = task_id
        map_data["result"] = result
        map_data["error_explanation"] = error_explanation
        map_data["computation_type"] = ViterbiComputationModel.JOB_TYPE
        map_data["viterbi_path_filename"] = file_viterbi_path
        map_data["region_filename"] = region_filename
        map_data["ref_seq_file"] = ref_seq_filename
        map_data["wga_seq_file"] = wga_seq_filename
        map_data["no_wag_seq_file"] = no_wag_seq_filename
        map_data["hmm_filename"] = hmm_filename
        map_data["chromosome"] = chromosome
        map_data["seq_size"] = seq_size
        map_data["number_of_gaps"] = number_of_gaps
        map_data["hmm_path_img"] = hmm_path_img
        map_data["extracted_sequences"] = extracted_sequences
        map_data["n_mixed_windows"] = n_mixed_windows
        map_data["window_type"] = window_type
        map_data["scheduler_id"] = scheduler_id
        map_data["start_region_idx"] = start_region_idx
        map_data["end_region_idx"] = end_region_idx

        return ViterbiComputationModel.build_from_map(map_data=map_data, save=save)

    @staticmethod
    def build_from_map(map_data, save):

        try:
            computation = ViterbiComputationModel.objects.get(task_id=map_data["task_id"])
            return computation
        except ObjectDoesNotExist:

            computation = ViterbiComputationModel()
            computation.task_id = map_data["task_id"]
            computation.result = map_data["result"]
            computation.error_explanation = map_data["error_explanation"]
            computation.computation_type = map_data["computation_type"]
            computation.file_viterbi_path = map_data["viterbi_path_filename"]
            computation.region_filename = map_data["region_filename"]
            computation.ref_seq_filename = map_data["ref_seq_file"]
            computation.wga_seq_filename = map_data["wga_seq_file"]
            computation.no_wag_seq_filename = map_data["no_wag_seq_file"]
            computation.hmm_filename = map_data["hmm_filename"]
            computation.chromosome = map_data["chromosome"]
            computation.seq_size = map_data["seq_size"]
            computation.number_of_gaps = map_data["number_of_gaps"]
            computation.hmm_path_img = map_data["hmm_path_img"]
            computation.extracted_sequences = map_data["extracted_sequences"]
            computation.n_mixed_windows = map_data["n_mixed_windows"]
            computation.window_type = map_data["window_type"]
            computation.scheduler_id = map_data["scheduler_id"]
            computation.start_region_idx = map_data["start_region_idx"]
            computation.end_region_idx = map_data["end_region_idx"]

            if save:
                computation.save()
                print("{0} saved computation: {1}".format(INFO, map_data["task_id"]))
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
            task = compute_viterbi_path_task.delay(hmm_name=hmm_name, chromosome=chromosome,
                                                   chromosome_index=data["chromosome_index"],
                                                   window_type=window_type, region_filename=region_filename,
                                                   hmm_filename=hmm_filename, sequence_size=None, n_sequences=1,
                                                   ref_seq_file=ref_seq_file, no_wga_seq_file=no_wga_seq_file,
                                                   wga_seq_file=wga_seq_file, remove_dirs=data["remove_dirs"],
                                                   use_spade=data["use_spade"], sequence_group=data["sequence_group"],
                                                   scheduler_id=data["scheduler_id"])
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
                                 use_spade=data["use_spade"], sequence_group=data["sequence_group"],
                                 scheduler_id=data["scheduler_id"])
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
        data_map["scheduler_id"] = result["scheduler_id"]
        data_map["start_region_idx"] = result["start_region_idx"]
        data_map["end_region_idx"] = result["end_region_idx"]
        return data_map


class KmerComputationModel(ComputationModel):
    """
    DB model for kmer calculation
    """

    # the type of the computation
    JOB_TYPE = JobType.KMER.name

    # the kmer field
    kmer = models.CharField(max_length=500, null=True)

    # how many times the kmer occured
    n_instances = models.IntegerField(default=0, null=True)

    # the repeat sequence the calculation corresponds to
    repeat_seq_id = models.ForeignKey(RepeatsModel, on_delete=models.CASCADE)

    class Meta(ComputationModel.Meta):
        db_table = 'kmer_computation'

    @staticmethod
    def compute(data):
        pass

    @staticmethod
    def get_invalid_map(task, result):
        data_map = dict()

        data_map["task_id"] = task.id
        data_map["result"] = JobResultEnum.FAILURE.name
        data_map["error_explanation"] = str(result)
        data_map["computation_type"] = KmerComputationModel.JOB_TYPE
        data_map['kmer'] = INVALID_STR
        data_map['n_instances'] = 0
        data_map['repeat_seq_id'] = INVALID_ITEM

        return data_map

    @staticmethod
    def build_from_data(task_id, result, error_explanation,
                        file_viterbi_path, save):
        map_data = dict()
        map_data["task_id"] = task_id
        map_data["result"] = result
        map_data["error_explanation"] = error_explanation
        map_data["computation_type"] = ViterbiComputationModel.JOB_TYPE
        return KmerComputationModel.build_from_map(map_data=map_data, save=save)

    @staticmethod
    def build_from_map(map_data, save):
        pass


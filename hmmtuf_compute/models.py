from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from compute_engine import INFO, INVALID_STR
from compute_engine.src.enumeration_types import JobType, JobResultEnum
from compute_engine.src.windows import WindowType
from hmmtuf import INVALID_ITEM
from hmmtuf.settings import USE_CELERY
from hmmtuf_home.models import ComputationModel
from hmmtuf_home.models import RepeatsModel
from hmmtuf_home.models import RegionModel
from hmmtuf_home.models import HMMModel
from hmmtuf_home.models import RegionGroupTipModel

from .tasks import compute_viterbi_path_task
from .tasks import compute_group_viterbi_path_task
from .tasks import compute_group_viterbi_path_all_task
from .ray_tasks import compute_group_viterbi_task


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
    # the type of the computation
    JOB_TYPE = JobType.GROUP_VITERBI.name

    # the tip used for the computation
    group_tip = models.ForeignKey(RegionGroupTipModel) #CharField(max_length=100, null=True)

    # the hmm model used for the computation
    hmm = models.ForeignKey(HMMModel)

    # number of regions
    number_regions = models.IntegerField(null=True)

    # start index of the first region in the group
    start_region_idx = models.IntegerField(null=True)

    # end index of the first region in the group
    end_region_idx = models.IntegerField(null=True)

    class Meta(ComputationModel.Meta):
        db_table = 'group_viterbi_computation'

    @staticmethod
    def get_as_map(model) -> dict:
        return model.__dict__

        """
        return {"task_id": model.task_id,
                "result": model.result,
                "error_explanation": model.error_explanation,
                "computation_type": GroupViterbiComputationModel.JOB_TYPE,
                "group_tip": model.group_tip,
                "hmm_name": model.hmm_name,
                "number_regions": model.number_regions,
                "start_region_idx": model.start_region_idx,
                "end_region_idx": model.end_region_idx}
        """

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
            computation.computation_type = GroupViterbiComputationModel.JOB_TYPE
            computation.hmm_name = map_data["hmm_name"]
            computation.group_tip = map_data["group_tip"]
            computation.number_regions = map_data["number_regions"]
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
                #task = compute_group_viterbi_path_task.delay(hmm_name=hmm_name,
                #                                             window_type=window_type,
                #                                             group_tip=data["group_tip"],
                #                                             remove_dirs=data["remove_dirs"],
                #                                             use_spade=data["use_spade"],
                #                                             sequence_group=data["sequence_group"])

                import uuid
                task_id = str(uuid.uuid4())
                compute_group_viterbi_task(task_id=task_id, hmm_name=hmm_name, use_spade=data["use_spade"],
                                           remove_dirs=data["remove_dirs"], group_tip=data["group_tip"])
            return task_id
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
        data_map["window_type"] = result["window_type"]
        data_map["group_tip"] = result["group_tip"]
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

    # the region the computed viterbi path corresponds to
    region = models.ForeignKey(RegionModel)

    # the hmm model used for the computation
    hmm = models.ForeignKey(max_length=500, null=True)

    # sequence size
    seq_size = models.IntegerField(null=True)

    # number of gaps
    number_of_gaps = models.IntegerField(null=True)

    # how many sequences used for the viterbi calculation
    extracted_sequences = models.IntegerField(default=1, null=True)

    class Meta(ComputationModel.Meta):
        db_table = 'viterbi_computation'

    @staticmethod
    def get_as_map(model) -> dict:
        return model.__dict__
        """
        return {"task_id": model.task_id,
                "result": model.result,
                "error_explanation": model.error_explanation,
                "computation_type": ViterbiComputationModel.JOB_TYPE,
                "viterbi_path_filename": model.file_viterbi_path.name,
                "region": model.region,
                "hmm": model.hmm,
                "seq_size": model.seq_size,
                "number_of_gaps": model.number_of_gaps,
                "extracted_sequences": model.extracted_sequences}
        """

    """
    @staticmethod
    def build_from_data(task_id, result, error_explanation,
                        file_viterbi_path, region,  hmm,
                        seq_size, number_of_gaps,  extracted_sequences,   save):

        map_data = dict()
        map_data["task_id"] = task_id
        map_data["result"] = result
        map_data["error_explanation"] = error_explanation
        map_data["computation_type"] = ViterbiComputationModel.JOB_TYPE
        map_data["viterbi_path_filename"] = file_viterbi_path
        map_data["region"] = region
        map_data["hmm"] = hmm
        map_data["seq_size"] = seq_size
        map_data["number_of_gaps"] = number_of_gaps
        map_data["extracted_sequences"] = extracted_sequences

        return ViterbiComputationModel.build_from_map(map_data=map_data, save=save)
    """

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
            computation.region = map_data["region"]
            computation.hmm = map_data["hmm"]
            computation.seq_size = map_data["seq_size"]
            computation.number_of_gaps = map_data["number_of_gaps"]
            computation.extracted_sequences = map_data["extracted_sequences"]

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
        data_map["region"] = result["region"]
        data_map["hmm"] = result["hmm"]
        data_map["seq_size"] = result["seq_size"]
        data_map["number_of_gaps"] = 0
        data_map["hmm_path_img"] = INVALID_ITEM
        data_map["extracted_sequences"] = 0

        return data_map

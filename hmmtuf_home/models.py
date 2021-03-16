from django.db import models
from django.core.files.storage import FileSystemStorage

from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine import DEFAULT_ERROR_EXPLANATION
from hmmtuf.settings import REGIONS_FILES_ROOT
from hmmtuf.settings import HMM_FILES_ROOT


def upload_hmm_file(instance, filename):
    return HMM_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])


def upload_region_file(instance, filename):
    return REGIONS_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])


class Computation(models.Model):

    RESULT_OPTIONS = ((JobResultEnum.PENDING.name, JobResultEnum.PENDING.name),
                      (JobResultEnum.SUCCESS.name, JobResultEnum.SUCCESS.name),
                      (JobResultEnum.FAILURE.name, JobResultEnum.FAILURE.name),
                      )

    # the task id of the computation
    task_id = models.CharField(max_length=300, primary_key=True)
    result = models.CharField(max_length=50, choices=RESULT_OPTIONS)
    error_explanation = models.CharField(max_length=500, default=DEFAULT_ERROR_EXPLANATION)
    computation_type = models.CharField(max_length=100)
    scheduler_id = models.CharField(max_length=200, null=True)

    class Meta:
        abstract = True


class FilesModel(models.Model):

    # a user defined name to distinguish
    name = models.CharField(max_length=100, unique=True)

    # the extension of the file
    extension = models.CharField(max_length=10)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s " % self.name


class HMMModel(FilesModel):

    file_hmm = models.FileField(upload_to=upload_hmm_file)

    class Meta(FilesModel.Meta):
        db_table = 'hmm_model'
        constraints = [
            models.UniqueConstraint(fields=['name', ], name='HMM unique  name constraint')
        ]

    def __str__(self):
        return "%s %s" % (self.name, self.file_hmm)

    @staticmethod
    def build_from_form(inst, form, save=True):
        # the object does not exist we can save the file
        file_loaded = form.file_loaded
        fs = FileSystemStorage(HMM_FILES_ROOT)
        file_loaded_name = form.name + '.json'
        filename = fs.save(file_loaded_name, file_loaded)

        inst.file_hmm = HMM_FILES_ROOT + file_loaded_name
        inst.name = form.name
        inst.extension = 'json'

        if save:
            inst.save()
        return inst


class RegionGroupTipModel(models.Model):

    # tip used to group region models
    tip = models.CharField(max_length=100, null=False, unique=True)

    # chromosome of the region group
    chromosome = models.CharField(max_length=10, null=False, unique=True)

    class Meta:
        db_table = 'region_group_tip'

    def __str__(self):
        return "%s" % self.tip


class RegionModel(FilesModel):

    # the file representing the region
    file_region = models.FileField(upload_to=upload_region_file, null=False)

    # the chromosome of the region
    chromosome = models.CharField(max_length=10, null=False)
    chromosome_index = models.IntegerField(default=-1, null=False)

    # files used to extract the region
    ref_seq_file = models.CharField(max_length=1000, null=False)
    wga_seq_file = models.CharField(max_length=1000, null=False)
    no_wga_seq_file = models.CharField(max_length=1000, null=False)

    # global start index of the region
    start_idx = models.IntegerField(null=False)

    # global end index of the region
    end_idx = models.IntegerField(null=False)

    # group the region belongs to
    group_tip = models.ForeignKey(RegionGroupTipModel, on_delete=models.CASCADE, null=False)

    class Meta(FilesModel.Meta):
        db_table = 'region_model'
        constraints = [
            models.UniqueConstraint(fields=['name', ], name='Region unique  name constraint')
        ]

    def __str__(self):
        return "%s %s" % (self.name, self.file_region)

    @staticmethod
    def build_from_form(inst, form, save=True):

        # the object does not exist we can save the file
        file_loaded = form.file_loaded
        fs = FileSystemStorage(REGIONS_FILES_ROOT)

        file_loaded_name = form.name + '_' + form.chromosome + '_' + str(form.start_idx)
        file_loaded_name += '_' + str(form.end_idx) + '.txt'
        filename = fs.save(file_loaded_name, file_loaded)

        inst.name = form.name
        inst.file_region = REGIONS_FILES_ROOT + file_loaded_name
        inst.name = form.name
        inst.extension = 'txt'
        inst.chromosome = form.chromosome
        inst.ref_seq_file = form.ref_seq_filename
        inst.wga_seq_file = form.wga_seq_filename
        inst.no_wga_seq_file = form.no_wga_seq_filename
        inst.start_idx = form.start_idx
        inst.end_idx = form.end_idx
        inst.chromosome_index = form.chromosome_idx

        if save:
            inst.save()
        return inst


class ViterbiSequenceGroupTip(models.Model):

    # tip used to group Viterbi sequence  models
    tip = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'viterbi_seq_group_tip'

    def __str__(self):
        return "%s" % self.tip


class ViterbiSequenceModel(models.Model):

    # the group tip
    group_tip = models.ForeignKey(ViterbiSequenceGroupTip, on_delete=models.CASCADE, null=False)

    # the file representing the region
    file_sequence = models.FileField(null=False)

    # region name
    region = models.ForeignKey(RegionModel, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'viterbi_seq_model'

    def __str__(self):
        return "%s" % self.group_tip









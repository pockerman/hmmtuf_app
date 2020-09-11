from django.db import models
from django.core.files.storage import FileSystemStorage

from compute_engine.job import JobResultEnum
from compute_engine import DEFAULT_ERROR_EXPLANATION
from hmmtuf.settings import REGIONS_FILES_ROOT
from hmmtuf.settings import HMM_FILES_ROOT

def upload_hmm_file(instance, filename):
    return HMM_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])

def upload_region_file(instance, filename):
    return REGIONS_FILES_ROOT + filename #'/'.join(['content', instance.user.username, filename])

# Create your models here.

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

    class Meta:
        abstract = True


class FilesModel(models.Model):

    id = models.AutoField(primary_key=True)

    # a user defined name to distinguish
    name = models.CharField(max_length=100)

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


class RegionModel(FilesModel):

    file_region = models.FileField(upload_to=upload_region_file)
    chromosome = models.CharField(max_length=10)
    ref_seq_file = models.CharField(max_length=1000)
    wga_seq_file = models.CharField(max_length=1000)
    no_wga_seq_file = models.CharField(max_length=1000)
    start_idx = models.IntegerField()
    end_idx = models.IntegerField()

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

        if save:
            inst.save()
        return inst



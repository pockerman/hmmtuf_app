from django.db import models

# Create your models here.

class FilesModel(models.Model):

    id = models.AutoField(primary_key=True)

    # name of the file
    filename = models.CharField(max_length=100)

    # a user defined name to distinguish
    name = models.CharField(max_length=100)

    # the extension of the file
    extension = models.CharField(max_length=10)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s %s"%(self.name, self.filename)


class HMMModel(FilesModel):

    class Meta(FilesModel.Meta):
        db_table = 'hmm_model'


class RegionModel(FilesModel):
    class Meta(FilesModel.Meta):
        db_table = 'region_model'



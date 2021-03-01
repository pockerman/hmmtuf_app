from django.db import models

# Create your models here.


class DistanceMetricType(models.Model):

    # string describing the class name
    # of the metric
    type = models.CharField(max_length=100, unique=True)

    # short name to refer to the metric
    short_cut = models.CharField(max_length=50, unique=True, default="INVALID")

    class Meta:
        db_table = 'distance_metric_type'

    def __str__(self):
        return "%s " % self.type


class DistanceSequenceType(models.Model):

    # a user defined name to distinguish
    type = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'distance_sequence_type'

    def __str__(self):
        return "%s " % self.type


class Repeats(models.Model):



    # the chromosome
    chromosome = models.CharField(max_length=100, unique=False)

    # the start index
    start_idx = models.IntegerField(unique=False)

    # the end index
    end_idx = models.IntegerField(unique=False)

    # the repeat sequence
    repeat_seq = models.CharField(max_length=500)

    # the state of the repeat comming from HMM
    hmm_state = models.CharField(max_length=50, default=None)

    # gc percentage
    gc = models.FloatField(default=0.0)

    class Meta:
        db_table = 'repeats'
        #unique_together = (('chromosome', 'start_idx', 'end_idx'),)
        #indexes = [
        #    models.Index(fields=['chromosome', 'start_idx', 'end_idx'], name='chromosome_start_end_idx'),
        #]




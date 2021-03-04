from django.db import models

# Create your models here.


class DistanceMetricType(models.Model):
    """
    DB model for distance metric types
    """

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

    CHOICES = [("NORMAL", "NORMAL"),
               ("PURINE", "PURINE"),
               ("AMINO", "AMINO"),
               ("WEAK_HYDROGEN", "WEAK_HYDROGEN"), ]

    # a user defined name to distinguish
    type = models.CharField(max_length=100, unique=True, choices=CHOICES)

    class Meta:
        db_table = 'distance_sequence_type'

    def __str__(self):
        return "%s " % self.type


class Repeats(models.Model):
    """
    DB model for repeats
    """
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


class RepeatsDistances(models.Model):
    """
    DB model for distances between the repeats
    """

    # the chromosome
    chromosome1 = models.CharField(max_length=100, unique=False)

    # the start index
    start_idx_1 = models.IntegerField(unique=False)

    # the end index
    end_idx_1 = models.IntegerField(unique=False)

    # the chromosome
    chromosome2 = models.CharField(max_length=100, unique=False)

    # the start index
    start_idx_2 = models.IntegerField(unique=False)

    # the end index
    end_idx_2 = models.IntegerField(unique=False)

    # the metric value computed
    value = models.FloatField()

    # the metric type used for the calculation
    metric_type = models.ForeignKey(DistanceMetricType, on_delete=models.CASCADE)

    # whether the calculation is based on
    # the original repeats NORMAL or the formed purine group PURINE
    # or amino group AMINO or weak hydrogen bond group WEAK_HYDROGEN
    sequence_type = models.ForeignKey(DistanceSequenceType, on_delete=models.CASCADE)

    # flag indicating if the metric is normalized
    is_normalized = models.BooleanField(default=True)

    class Meta:
        db_table = 'repeats_distances'











from django.contrib import admin
from .models import DistanceMetricType
from .models import DistanceSequenceType
from .models import Repeats
from .models import RepeatsDistances


class DistanceMetricTypeAdmin(admin.ModelAdmin):
    fields = ['type', 'short_cut', ]
    list_display = ('type', 'short_cut')


class DistanceSequenceTypeAdmin(admin.ModelAdmin):
    fields = ['type', ]
    list_display = ('type',)


class RepeatsAdmin(admin.ModelAdmin):
    fields = ['chromosome',  'start_idx', 'end_idx', 'hmm_state', 'gc', 'repeat_seq', ]
    list_display = ('chromosome',  'start_idx', 'end_idx', 'hmm_state', 'gc', 'repeat_seq')


class RepeatsDistancesAdmin(admin.ModelAdmin):
    fields = ['chromosome1', 'start_idx_1', 'end_idx_1',
              'chromosome2', 'start_idx_2', 'end_idx_2',
              'value', 'metric_type', 'sequence_type', 'is_normalized']
    list_display = ('chromosome1', 'start_idx_1', 'end_idx_1',
                    'chromosome2', 'start_idx_2', 'end_idx_2',
                    'value', 'metric_type', 'sequence_type', 'is_normalized')


admin.site.register(DistanceMetricType, DistanceMetricTypeAdmin)
admin.site.register(DistanceSequenceType, DistanceSequenceTypeAdmin)
admin.site.register(Repeats, RepeatsAdmin)
admin.site.register(RepeatsDistances, RepeatsDistancesAdmin)

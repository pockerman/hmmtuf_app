from django.contrib import admin
from .models import DistanceMetricType
from .models import DistanceSequenceType
from .models import Repeats


class DistanceMetricTypeAdmin(admin.ModelAdmin):
    fields = ['type', 'short_cut', ]
    list_display = ('type', 'short_cut')


class DistanceSequenceTypeAdmin(admin.ModelAdmin):
    fields = ['type', ]
    list_display = ('type',)


class RepeatsAdmin(admin.ModelAdmin):
    fields = ['chromosome',  'start_idx', 'end_idx', 'hmm_state', 'gc', 'repeat_seq',  ]
    list_display = ('chromosome',  'start_idx', 'end_idx', 'hmm_state', 'gc', 'repeat_seq')


admin.site.register(DistanceMetricType, DistanceMetricTypeAdmin)
admin.site.register(DistanceSequenceType, DistanceSequenceTypeAdmin)
admin.site.register(Repeats, RepeatsAdmin)

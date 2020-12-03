from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import ViterbiComputation
from .models import MultiViterbiComputation
from .models import GroupViterbiComputation
from .models import ScheduleComputation


class ViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'region_filename', 'hmm_filename',
              'result', 'error_explanation', 'ref_seq_filename',
              'wga_seq_filename', 'no_wag_seq_filename']
    list_display = ('task_id', 'chromosome', 'region_filename', 'result', 'error_explanation')


class MultiViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'hmm_filename', 'result', 'error_explanation',
              'ref_seq_filename', 'wga_seq_filename', 'no_wag_seq_filename']
    list_display = ('task_id', 'result', 'error_explanation')


class GroupViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'hmm_filename', 'result', 'error_explanation', 'group_tip', ]
    list_display = ('task_id', 'result', 'error_explanation', 'group_tip', 'scheduler_id', 'number_regions')


class ScheduleComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'result', 'error_explanation', ]
    list_display = ('task_id', 'result', 'error_explanation', )


admin.site.register(ViterbiComputation, ViterbiComputationAdmin)
admin.site.register(MultiViterbiComputation, MultiViterbiComputationAdmin)
admin.site.register(GroupViterbiComputation, GroupViterbiComputationAdmin)
admin.site.register(ScheduleComputation, ScheduleComputationAdmin)


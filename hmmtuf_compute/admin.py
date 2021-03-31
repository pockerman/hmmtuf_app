from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import ViterbiComputationModel
from .models import GroupViterbiComputationModel


class ViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'region_filename', 'hmm_filename',
              'result', 'error_explanation', 'ref_seq_filename',
              'wga_seq_filename', 'no_wag_seq_filename']
    list_display = ('task_id', 'chromosome', 'region_filename', 'result', 'error_explanation')


class GroupViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'hmm_filename', 'result', 'error_explanation', 'group_tip', ]
    list_display = ('task_id', 'result', 'error_explanation', 'group_tip', 'scheduler_id', 'number_regions')


admin.site.register(ViterbiComputationModel, ViterbiComputationAdmin)
admin.site.register(GroupViterbiComputationModel, GroupViterbiComputationAdmin)



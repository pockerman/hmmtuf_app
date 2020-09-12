from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import ViterbiComputation
from .models import MultiViterbiComputation


class ViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'region_filename', 'hmm_filename', 'result', 'error_explanation', 'wga_seq_filename', 'no_wag_seq_filename']
    list_display = ('task_id', 'result', 'error_explanation')


class MultiViterbiComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'region_filename', 'hmm_filename', 'result', 'error_explanation']
    list_display = ('task_id', 'result', 'error_explanation')


admin.site.register(ViterbiComputation, ViterbiComputationAdmin)
admin.site.register(MultiViterbiComputation, MultiViterbiComputationAdmin)


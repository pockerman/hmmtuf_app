from django.contrib import admin

# Register your models here.
from .models import ExtractRegionComputation

class ExtractRegionComputationAdmin(admin.ModelAdmin):
    fields = ['task_id', 'computation_type', 'result', 'error_explanation']
    list_display = ('task_id', 'computation_type', 'result', 'error_explanation',)


admin.site.register(ExtractRegionComputation, ExtractRegionComputationAdmin)


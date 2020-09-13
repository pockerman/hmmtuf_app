from django.contrib import admin

# Register your models here.
from .models import HMMModel
from .models import RegionModel
from .models import RegionGroupTipModel


class HMMModelAdmin(admin.ModelAdmin):
    fields = ['name', 'file_hmm', 'extension']
    list_display = ('name', 'extension')


class RegionModelAdmin(admin.ModelAdmin):
    fields = ['name', 'chromosome', 'file_region', 'wga_seq_file', 'no_wga_seq_file', 'extension', ]
    list_display = ('name', 'chromosome', 'start_idx', 'end_idx', 'group_tip')


class RegionGroupTipModelAdmin(admin.ModelAdmin):
    fields = ['tip']
    list_display = ('id', 'tip')


admin.site.register(HMMModel, HMMModelAdmin)
admin.site.register(RegionModel, RegionModelAdmin)
admin.site.register(RegionGroupTipModel, RegionGroupTipModelAdmin)

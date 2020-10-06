from django.contrib import admin

# Register your models here.
from .models import HMMModel
from .models import RegionModel
from .models import RegionGroupTipModel
from .models import ViterbiSequenceGroupTip
from .models import ViterbiSequenceModel


class HMMModelAdmin(admin.ModelAdmin):
    fields = ['name', 'file_hmm', 'extension']
    list_display = ('name', 'file_hmm')


class RegionModelAdmin(admin.ModelAdmin):
    fields = ['name', 'chromosome', 'chromosome_index',
              'file_region', 'wga_seq_file', 'no_wga_seq_file', 'extension', ]
    list_display = ('name', 'chromosome', 'start_idx', 'end_idx', 'group_tip')


class RegionGroupTipModelAdmin(admin.ModelAdmin):
    fields = ['tip', 'chromosome']
    list_display = ('id', 'tip', 'chromosome')


class ViterbiSequenceGroupTipModelAdmin(admin.ModelAdmin):
    fields = ['tip']
    list_display = ('id', 'tip')


class ViterbiSequenceModelAdmin(admin.ModelAdmin):
    fields = ['group_tip', 'file_sequence']
    list_display = ('id', 'group_tip', 'file_sequence', 'region')


admin.site.register(HMMModel, HMMModelAdmin)
admin.site.register(RegionModel, RegionModelAdmin)
admin.site.register(RegionGroupTipModel, RegionGroupTipModelAdmin)
admin.site.register(ViterbiSequenceGroupTip, ViterbiSequenceGroupTipModelAdmin)
admin.site.register(ViterbiSequenceModel, ViterbiSequenceModelAdmin)

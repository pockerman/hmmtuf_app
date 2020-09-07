from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import HMMModel
from .models import RegionModel


class HMMModelAdmin(admin.ModelAdmin):
    fields = ['name', 'file_hmm', 'extension']
    list_display = ('name', 'extension')


class RegionModelAdmin(admin.ModelAdmin):
    fields = ['name', 'chromosome', 'file_region', 'extension']
    list_display = ('name',  'extension')


admin.site.register(HMMModel, HMMModelAdmin)
admin.site.register(RegionModel, RegionModelAdmin)

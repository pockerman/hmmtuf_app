from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

# Create your views here.


def extract_region_view(request):
    template = loader.get_template('region_extractor/extract_region_view.html')
    context = {"outlier_remove_names": ["None", "Mean Cutoff"]}
    return HttpResponse(template.render(context, request))


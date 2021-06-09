from django.shortcuts import render
from django.shortcuts import redirect
from django.template import loader
from django.http import HttpResponse
from compute_engine import OK

from .forms import LoadBedFile


def load_bed_file_view(request):

    if request.method == 'POST':

        form = LoadBedFile()
        if form.check(request=request) is not OK:
            return form.response

        # schedule the computation

    template = loader.get_template('bed_comparator/load_bed_file_view.html')
    return HttpResponse(template.render({"error_name_exist": "The HMM name exists"}, request))
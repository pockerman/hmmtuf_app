import uuid
import os

from django.shortcuts import render
from django.shortcuts import redirect
from django.template import loader
from django.http import HttpResponse
from compute_engine import OK
from webapp_utils.helpers import make_bed_compare_path, make_bed_compare_filename_path, make_viterbi_compare_filename_path
from .forms import LoadBedFile
from .models import BedComparisonModel


template_ids = dict()
template_ids['load_bed_file_view'] = 'bed_comparator/load_bed_file_view.html'
template_ids['success_load_bed_view'] = 'bed_comparator/success_schedule_bed_compute_view.html'

def load_bed_file_view(request):

    template = loader.get_template(template_ids[load_bed_file_view.__name__])
    if request.method == 'POST':

        #import pdb
        #pdb.set_trace()
        form = LoadBedFile(template_html=template)
        if form.check(request=request) is not OK:
            return form.response

        kwargs = form.as_dict()

        # generate a new task id
        task_id = str(uuid.uuid4())

        dir_path = make_bed_compare_path(task_id=task_id)

        try:
            os.makedirs(name=dir_path)
        except Exception as e:
            print("Could not create directory")
            return redirect('/')

        print(kwargs['bed_filename'].temporary_file_path())
        print(kwargs['bed_filename'].name)

        # generate a new model and save
        model = BedComparisonModel()
        model.task_id = task_id

        path_bed = make_bed_compare_filename_path(task_id=task_id, bed_name=kwargs['bed_filename'].name)
        path_viterbi = make_viterbi_compare_filename_path(task_id=task_id, viterbi_name=kwargs['viterbi_filename'].name)

        model.viterbi_filename = path_bed
        model.bed_filename = path_viterbi

        model.save()
        #task_id = BedComparisonModel.compute(data=kwargs)


        return redirect('success_load_bed_view', task_id=task_id)

    return HttpResponse(template.render({"error_name_exist": "The HMM name exists"}, request))


def success_load_bed_view(request, task_id: str) -> HttpResponse:
    """
    Serves the success or pending view for
    a bed comparison computation. The compuation is
    identified by the task_id
    """
    template = loader.get_template(template_ids[success_load_bed_view.__name__])



    return HttpResponse(template.render({"show_get_results_button": True, "task_id": task_id}, request))



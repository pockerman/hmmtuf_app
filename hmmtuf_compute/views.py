from django.shortcuts import render
from django.http import HttpResponse

from django.template import loader
from django.shortcuts import redirect
from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf.settings import VITERBI_PATHS_FILES_URL
from hmmtuf.celery import celery_app
from file_loader.models import HMMModel, RegionModel

# Create your views here.
from . import models
from . import utils
from . import helpers
from . import forms


def schedule_computation_view(request):
    """
    schedules a computation. This is done by asking the user
    to specify a region name and an HMM name to compute the computation.
    This function wraps the POST/GET requests
    """

    if request.method == 'POST':

        #import pdb
        #pdb.set_trace()
        kwargs = forms.wrap_data_for_viterbi_calculation(request=request,
                                                         viterbi_path_files_root=VITERBI_PATHS_FILES_ROOT)

        task = models.ViterbiComputation.compute(data=kwargs)

        # return the id for the computation
        return redirect('view_viterbi_path', task_id=task.id)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created. Create HMM models",}
        template = loader.get_template('hmmtuf_compute/schedule_viterbi_compute_view.html')
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    # get the regions we have
    regions = RegionModel.objects.all()

    if len(regions) == 0:
        context = {"error_empty_region_list": "Regions have not been created. Upload a region file", }
        template = loader.get_template('hmmtuf_compute/schedule_viterbi_compute_view.html')
        return HttpResponse(template.render(context, request))

    region_names = []
    for item in regions:
        region_names.append(item.name)

    context = {"region_names": region_names,
               "hmm_names": hmm_names,
               'window_names': helpers.WindowType.get_window_types(), }
    template = loader.get_template('hmmtuf_compute/schedule_viterbi_compute_view.html')
    return HttpResponse(template.render(context, request))


def view_viterbi_path(request, task_id):

    # check if the computation is ready
    # if yes collect the results
    # otherwise return the html
    task = celery_app.AsyncResult(task_id)
    template = loader.get_template('hmmtuf_compute/viterbi_result_view.html')
    context = {'task_status': task.status}

    if task.status == 'PENDING':
        show_get_results_button = True
        #result, viterbi_calculation = task.get()

        #if models.ViterbiComputation.filter(task_id=task.id) is not None:
        #    pass
        #else:
        #    viterbi_calculation.save()

        context.update({'show_get_results_button': show_get_results_button,
                        'task_id': task_id})
        return HttpResponse(template.render(context, request))
    elif task.status == 'SUCCESS':
        result = task.get()
        print("Result is: ", result)
        models.ViterbiComputation.build_from_map(result, save=True)

        context.update(result)
        return HttpResponse(template.render(context, request))
    elif task.status == 'FAILURE':
        result = task.get()
        models.ViterbiComputation.build_from_map(result, save=True)
        context.update({'error_task_failed': True,
                        'task_id': task_id})
        return HttpResponse(template.render(context, request))

    return HttpResponse(template.render(context, request))


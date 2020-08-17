from django.shortcuts import render
from django.http import HttpResponse

from django.template import loader
from django.shortcuts import redirect
from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf.settings import VITERBI_PATHS_FILES_URL
from hmmtuf.celery import celery_app
from file_loader.models import HMMModel

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

        kwargs = forms.wrap_data_for_viterbi_calculation(request=request,
                                                         viterbi_path_files_root=VITERBI_PATHS_FILES_ROOT)

        task = models.Computation.compute(utils.ComputationEnum.VITERBI, data=kwargs)

        # return the id for the computation
        return redirect('view_viterbi_path', task_id=task.id)

    # get the hmm names we have

    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created. Create HMM models",}
        template = loader.get_template('hmmtuf_compute/schedule_viterbi_compute_view.html')
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    context = {"region_names": ["Region1", "Region2", "Region3"],
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
        context.update({'show_get_results_button': show_get_results_button,
                        'task_id': task_id})
        return HttpResponse(template.render(context, request))
    elif task.status == 'SUCCESS':
        result = task.get()

        context.update(result)
        return HttpResponse(template.render(context, request))

    return HttpResponse(template.render(context, request))


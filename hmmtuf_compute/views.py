from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf.celery import celery_app
from hmmtuf_home.models import HMMModel, RegionModel
from compute_engine.windows import WindowType
from compute_engine import INVALID_STR, INFO
from compute_engine.job import JobType, JobResultEnum

# Create your views here.
from . import models
from . import forms


def learn_d3(request):
    template = loader.get_template('hmmtuf_compute/learn_d3.html')
    context={}
    return HttpResponse(template.render(context, request))


def schedule_computation_view(request):
    """
    schedules a computation. This is done by asking the user
    to specify a region name and an HMM name to compute the computation.
    This function wraps the POST/GET requests
    """

    if request.method == 'POST':

        kwargs = forms.wrap_data_for_viterbi_calculation(request=request,
                                                         viterbi_path_files_root=VITERBI_PATHS_FILES_ROOT)

        task = models.ViterbiComputation.compute(data=kwargs)

        # return the id for the computation
        return redirect('view_viterbi_path', task_id=task.id)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        link = ''
        context = {"error_empty_hmm_list": "HMM models have not been created."}
        template = loader.get_template('hmmtuf_compute/schedule_viterbi_compute_view.html')
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    # get the regions we have
    regions = RegionModel.objects.all()

    if len(regions) == 0:
        context = {"error_empty_region_list": "Regions have not been created.", }
        template = loader.get_template('hmmtuf_compute/schedule_viterbi_compute_view.html')
        return HttpResponse(template.render(context, request))

    region_names = []
    for item in regions:
        region_names.append(item.name)

    context = {"region_names": region_names,
               "hmm_names": hmm_names,
               'window_names': WindowType.get_window_types(), }

    template = loader.get_template('hmmtuf_compute/schedule_viterbi_compute_view.html')
    return HttpResponse(template.render(context, request))


def view_viterbi_path(request, task_id):

    template = loader.get_template('hmmtuf_compute/viterbi_result_view.html')
    try:

        print("{0} trying to get task: {1}".format(INFO, task_id))

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.ViterbiComputation.objects.get(task_id=task_id)

        if task.result == 'FAILURE':
            context = {'error_task_failed': True, "error_message": task.error_explanation,
                            'task_id': task_id, "computation": task}
            return HttpResponse(template.render(context, request))
        else:

            context = {'task_status': task.result, "computation": task}
            return HttpResponse(template.render(context, request))
    except ObjectDoesNotExist:

        print("{0}  task: {1} didn't exist".format(INFO, task_id))
        #import pdb
        #pdb.set_trace()
        # try to ask celery

        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        context = {'task_status': task.status}

        if task.status == 'PENDING':
            show_get_results_button = True

            context.update({'show_get_results_button': show_get_results_button,
                            'task_id': task_id})
            return HttpResponse(template.render(context, request))
        elif task.status == 'SUCCESS':
            result = task.get()

            computation = models.ViterbiComputation.build_from_map(result, save=True)
            context.update({"computation": computation})

            return HttpResponse(template.render(context, request))
        elif task.status == 'FAILURE':

            result = task.get(propagate=False)

            map = {}

            map["task_id"] = task.id
            map["result"] = JobResultEnum.FAILURE.name
            map["error_explanation"] = str(result)
            map["computation_type"] = JobType.VITERBI.name
            map["viterbi_path_filename"] = INVALID_STR
            map["region_filename"] = INVALID_STR
            map["hmm_filename"] = INVALID_STR
            map["chromosome"] = INVALID_STR
            map["seq_size"] = 0
            map["ref_seq_file"] = INVALID_STR
            map["wga_seq_file"] = INVALID_STR
            map["no_wag_seq_file"] = INVALID_STR
            map["number_of_gaps"] = 0
            map["hmm_path_img"] = None
            map["extracted_sequences"] = 0
            map["n_mixed_windows"] = 0
            map["window_type"] = INVALID_STR

            computation = models.ViterbiComputation.build_from_map(map, save=True)
            context.update({'error_task_failed': True, "error_message": str(result),
                            'task_id': task_id, "computation": computation})
            return HttpResponse(template.render(context, request))



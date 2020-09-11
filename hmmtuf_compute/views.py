from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from compute_engine.windows import WindowType
from compute_engine import INVALID_STR, INFO, OK
from compute_engine.job import JobType, JobResultEnum
from compute_engine.utils import read_json, extract_file_names, extract_path

from hmmtuf import VITERBI_PATH_FILENAME
from hmmtuf.settings import BASE_DIR
from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf.celery import celery_app
from hmmtuf_home.models import HMMModel, RegionModel

# Create your views here.
from . import models
from . import forms


def learn_d3(request):
    template = loader.get_template('hmmtuf_compute/learn_d3.html')
    context={}
    return HttpResponse(template.render(context, request))


def schedule_hmm_multi_viterbi_view(request):
    """
    Schedule a multi-region Viterbi computation.
    """

    configuration = read_json(filename="%s/config.json" % BASE_DIR)
    reference_files_names, wga_files_names, \
    nwga_files_names = extract_file_names(configuration=configuration)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"no_models_error_msg": "HMM models have not been created."}
        template = loader.get_template('hmmtuf_compute/schedule_hmm_multi_viterbi_view.html')
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    context = {"reference_files_names": reference_files_names,
               "hmm_names": hmm_names, }

    if request.method == 'POST':

        form = forms.MultipleViterbiComputeForm(template_html='hmmtuf_compute/schedule_hmm_multi_viterbi_view.html',
                                                configuration=configuration,
                                                context=context)

        result = form.check(request=request)
        if result is not OK:
            return form.response

        kwargs = form.as_map()
        kwargs['viterbi_path_filename'] = VITERBI_PATH_FILENAME
        task_id = models.MultiViterbiComputation.compute(data=kwargs)

        # return the id for the computation
        return redirect('view_multi_viterbi_path', task_id=task_id)

    template = loader.get_template('hmmtuf_compute/schedule_hmm_multi_viterbi_view.html')
    return HttpResponse(template.render(context, request))


def view_multi_viterbi_path(request, task_id):

    """
    View the Viterbi path of a multi-region compuation
    """

    template = loader.get_template('hmmtuf_compute/multi_viterbi_path_view.html')
    try:

        print("{0} trying to get task: {1}".format(INFO, task_id))

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.MultiViterbiComputation.objects.get(task_id=task_id)

        if task.result == 'FAILURE':
            context = {'error_task_failed': True,
                       "error_message": task.error_explanation,
                       'task_id': task_id,
                       "computation": task}
            return HttpResponse(template.render(context, request))
        elif task.result == JobResultEnum.PENDING.name:

            context = {'show_get_results_button': True,
                       'task_id': task_id,
                       'task_status': JobResultEnum.PENDING.name}
            return HttpResponse(template.render(context, request))

        else:

            context = {'task_status': task.result, "computation": task}
            return HttpResponse(template.render(context, request))
    except ObjectDoesNotExist:

        print("{0}  task: {1} didn't exist".format(INFO, task_id))

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        context = {'task_status': task.status}

        if task.status == 'PENDING':

            context.update({'show_get_results_button': True,
                            'task_id': task_id})
            return HttpResponse(template.render(context, request))
        elif task.status == 'SUCCESS':
            result = task.get()

            computation = models.MultiViterbiComputation.build_from_map(result, save=True)
            context.update({"computation": computation})

            return HttpResponse(template.render(context, request))
        elif task.status == 'FAILURE':

            result = task.get(propagate=False)

            map = dict()
            map["task_id"] = task.id
            map["result"] = JobResultEnum.FAILURE.name
            map["error_explanation"] = str(result)
            map["computation_type"] = JobType.MULTI_VITERBI.name
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

            computation = models.MultiViterbiComputation.build_from_map(map, save=True)
            context.update({'error_task_failed': True, "error_message": str(result),
                            'task_id': task_id, "computation": computation})
            return HttpResponse(template.render(context, request))


def schedule_hmm_viterbi_computation_view(request):
    """
    Schedules a region Viterbi computation.
    """

    if request.method == 'POST':

        kwargs = forms.wrap_data_for_viterbi_calculation(request=request)
        task_id = models.ViterbiComputation.compute(data=kwargs)

        # return the id for the computation
        return redirect('view_viterbi_path', task_id=task_id)

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
            context = {'error_task_failed': True,
                       "error_message": task.error_explanation,
                        'task_id': task_id, "computation": task}
            return HttpResponse(template.render(context, request))
        else:
            context = {'task_status': task.result, "computation": task}
            return HttpResponse(template.render(context, request))
    except ObjectDoesNotExist:

        print("{0}  task: {1} didn't exist".format(INFO, task_id))

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)
        context = {'task_status': task.status}

        if task.status == 'PENDING':

            context.update({'show_get_results_button': True,
                            'task_id': task_id})
            return HttpResponse(template.render(context, request))
        elif task.status == 'SUCCESS':
            result = task.get()

            computation = models.ViterbiComputation.build_from_map(result, save=True)
            context.update({"computation": computation})

            return HttpResponse(template.render(context, request))
        elif task.status == 'FAILURE':

            result = task.get(propagate=False)

            map = dict()

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
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id, "computation": computation})
            return HttpResponse(template.render(context, request))



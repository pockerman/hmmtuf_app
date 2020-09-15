from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from compute_engine.windows import WindowType
from compute_engine import INVALID_STR, INFO, OK
from compute_engine.job import JobType, JobResultEnum
from compute_engine.utils import read_json, extract_file_names, get_sequence_name, get_tdf_file

from hmmtuf import VITERBI_PATH_FILENAME
from hmmtuf import INVALID_TASK_ID, INVALID_ITEM
from hmmtuf.helpers import get_configuration
from hmmtuf.helpers import make_bed_path

from hmmtuf.celery import celery_app
from hmmtuf_home.models import HMMModel, RegionModel, RegionGroupTipModel

# Create your views here.
from . import models
from . import forms


def success_schedule_multi_viterbi_computation_view(request, task_id):
    template = loader.get_template('hmmtuf_compute/success_schedule_multi_viterbi_computation_view.html')

    context = {"task_id": task_id}
    if task_id == INVALID_TASK_ID:
        error_msg = "Task does not exist"
        context.update({"error_msg": error_msg})
    return HttpResponse(template.render(context, request))


def schedule_hmm_multi_viterbi_view(request):
    """
    Schedule a multi-region Viterbi computation.
    """

    configuration = get_configuration()
    reference_files_names, wga_files_names, \
    nwga_files_names = extract_file_names(configuration=configuration)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created."}
        template = loader.get_template('hmmtuf_compute/schedule_multi_viterbi__compute_view.html')
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    group_tips = RegionGroupTipModel.objects.all()

    context = {"reference_files_names": reference_files_names,
               "hmm_names": hmm_names, "group_tips": group_tips}

    if request.method == 'POST':

        form = forms.MultipleViterbiComputeForm(template_html='hmmtuf_compute/schedule_multi_viterbi__compute_view.html',
                                                configuration=configuration,
                                                context=context)

        result = form.check(request=request)
        if result is not OK:
            return form.response

        kwargs = form.as_map()
        kwargs['viterbi_path_filename'] = VITERBI_PATH_FILENAME
        task_id = models.MultiViterbiComputation.compute(data=kwargs)

        # return the id for the computation
        return redirect('success_schedule_multi_viterbi_computation_view', task_id=task_id)

    template = loader.get_template('hmmtuf_compute/schedule_multi_viterbi__compute_view.html')
    return HttpResponse(template.render(context, request))


def view_multi_viterbi_path(request, task_id):

    """
    View the Viterbi path of a multi-region compuation
    """
    #import pdb
    #pdb.set_trace()
    template = loader.get_template('hmmtuf_compute/multi_viterbi_result_view.html')
    try:

        print("{0} trying to get task: {1}".format(INFO, task_id))

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.MultiViterbiComputation.objects.get(task_id=task_id)
        context = _get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))

    except ObjectDoesNotExist:

        print("{0}  task: {1} didn't exist".format(INFO, task_id))

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        if task is None:
            return success_schedule_multi_viterbi_computation_view(request, task_id=INVALID_TASK_ID)

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
            data_map = models.MultiViterbiComputation.get_invalid_map(task=task, result=result)
            computation = models.MultiViterbiComputation.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id,
                            "computation": computation})
            return HttpResponse(template.render(context, request))


def success_schedule_viterbi_computation_view(request, task_id):
    template = loader.get_template('hmmtuf_compute/success_schedule_viterbi_computation_view.html')

    context = {"task_id": task_id}
    if task_id == INVALID_TASK_ID:
        error_msg = "Task does not exist"
        context.update({"error_msg": error_msg})
    return HttpResponse(template.render(context, request))


def schedule_hmm_viterbi_computation_view(request):
    """
    Schedules a region Viterbi computation.
    """

    if request.method == 'POST':

        form = forms.ViterbiComputeForm(template_html=INVALID_ITEM,
                                        configuration=INVALID_ITEM,
                                        context=INVALID_ITEM)
        form.check(request=request)
        task_id = models.ViterbiComputation.compute(data=form.as_map())

        # return the id for the computation
        return redirect('success_schedule_viterbi_computation_view', task_id=task_id)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
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
        context = _get_result_view_context(task=task, task_id=task_id)
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
            data_map = models.ViterbiComputation.get_invalid_map(task=task, result=result)
            computation = models.ViterbiComputation.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id, "computation": computation})

            return HttpResponse(template.render(context, request))


def _get_result_view_context(task, task_id):

    if task.result == JobResultEnum.FAILURE.name:
        context = {'error_task_failed': True,
                   "error_message": task.error_explanation,
                   'task_id': task_id, "computation": task}
        return context
    elif task.result == JobResultEnum.PENDING.name:

        context = {'show_get_results_button': True,
                   'task_id': task_id,
                   'task_status': JobResultEnum.PENDING.name}

        return context

    else:

        configuration = get_configuration()
        wga_name = task.wga_seq_filename.split("/")[-1]
        wga_seq_name = get_sequence_name(configuration=configuration, seq=wga_name)
        wga_tdf_file = get_tdf_file(configuration=configuration, seq=wga_name)

        no_wga_name = task.no_wag_seq_filename.split("/")[-1]
        no_wga_seq_name = get_sequence_name(configuration=configuration, seq=no_wga_name)
        no_wga_tdf_file = get_tdf_file(configuration=configuration, seq=no_wga_name)

        context = {'task_status': task.result,
                   "computation": task,
                   "wga_seq_name": wga_seq_name,
                   "no_wga_seq_name": no_wga_seq_name,
                   "wga_tdf_file": wga_tdf_file,
                   "no_wga_tdf_file": no_wga_tdf_file,
                   "normal_bed_url": make_bed_path(task_id=task_id, bed_name='normal.bed'),
                   "tuf_bed_url": make_bed_path(task_id=task_id, bed_name='tuf.bed'),
                   "deletion_bed_url": make_bed_path(task_id=task_id, bed_name="deletion.bed"),
                   "duplication_bed_url": make_bed_path(task_id=task_id, bed_name="duplication.bed"),
                   "gap_bed_url": make_bed_path(task_id=task_id, bed_name="gap.bed"),
                   "repeats_bed_url": make_bed_path(task_id=task_id, bed_name="rep.bed"),
                   "quad_bed_url": make_bed_path(task_id=task_id, bed_name="quad.bed"),
                   "tdt_bed_url": make_bed_path(task_id=task_id, bed_name="tdt.bed")}
        return context



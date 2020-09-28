from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from compute_engine.windows import WindowType
from compute_engine import OK


from hmmtuf import INVALID_TASK_ID, INVALID_ITEM, ENABLE_SPADE
from hmmtuf.helpers import get_configuration
from hmmtuf.celery import celery_app
from hmmtuf_home.models import HMMModel, RegionModel, RegionGroupTipModel, ViterbiSequenceGroupTip

# Create your views here.
from . import models
from . import forms
from . view_helpers import get_result_view_context
from . view_helpers import view_viterbi_path_exception_context
from . view_helpers import handle_success_view


def success_schedule_group_viterbi_compute_view(request, task_id):

    template_html = 'hmmtuf_compute/success_schedule_group_viterbi_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def schedule_group_viterbi_compute_view(request):

    template_html = 'hmmtuf_compute/schedule_group_viterbi_compute_view.html'
    template = loader.get_template(template_html)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created."}
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    group_tips = RegionGroupTipModel.objects.all()
    context = {"hmm_names": hmm_names, "group_tips": group_tips}

    if ENABLE_SPADE:
        context.update({"use_spade": True})

    if request.method == 'POST':

        form = forms.GroupViterbiComputeForm(template_html=template_html, context=context)

        result = form.check(request=request)
        if result is not OK:
            return form.response

        kwargs = form.as_map()
        task_id = models.GroupViterbiComputation.compute(data=kwargs)

        # return the id for the computation
        return redirect('success_schedule_group_viterbi_compute_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


def view_group_viterbi_path(request, task_id):

    """
    View the Viterbi path of a multi-region computation
    """

    template_html = 'hmmtuf_compute/group_viterbi_result_view.html'
    template = loader.get_template(template_html)

    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.GroupViterbiComputation.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))

    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        if task is None:
            return success_schedule_multi_viterbi_compute_view(request, task_id=INVALID_TASK_ID)

        context = view_viterbi_path_exception_context(task=task, task_id=task_id,
                                                      model=models.GroupViterbiComputation.__name__)
        return HttpResponse(template.render(context, request))


def success_schedule_multi_viterbi_compute_view(request, task_id):

    template_html = 'hmmtuf_compute/success_schedule_multi_viterbi_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def schedule_multi_viterbi_compute_view(request):
    """
    Schedule a multi-region Viterbi computation.
    """

    template_html = 'hmmtuf_compute/schedule_multi_viterbi_compute_view.html'
    configuration = get_configuration()

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created."}
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    group_tips = RegionGroupTipModel.objects.all()
    context = {"hmm_names": hmm_names, "group_tips": group_tips}

    if ENABLE_SPADE:
        context.update({"use_spade": True})

    if request.method == 'POST':

        form = forms.MultipleViterbiComputeForm(template_html=template_html,
                                                configuration=configuration,
                                                context=context)

        result = form.check(request=request)
        if result is not OK:
            return form.response

        task_id = models.MultiViterbiComputation.compute(data=form.as_map())

        # return the id for the computation
        return redirect('success_schedule_multi_viterbi_computation_view', task_id=task_id)

    template = loader.get_template(template_html)
    return HttpResponse(template.render(context, request))


def view_multi_viterbi_path(request, task_id):

    """
    View the Viterbi path of a multi-region computation
    """
    template_html = 'hmmtuf_compute/multi_viterbi_result_view.html'
    template = loader.get_template(template_html)

    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.MultiViterbiComputation.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))

    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        if task is None:
            return success_schedule_multi_viterbi_compute_view(request, task_id=INVALID_TASK_ID)

        context = view_viterbi_path_exception_context(task=task, task_id=task_id,
                                                      model=models.MultiViterbiComputation.__name__)
        return HttpResponse(template.render(context, request))


def success_schedule_viterbi_compute_view(request, task_id):
    """
    Success redirect after scheduling a Viterbi path computation
    """

    template_html = 'hmmtuf_compute/success_schedule_viterbi_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def schedule_hmm_viterbi_compute_view(request):
    """
    Schedule a region Viterbi computation.
    """

    # the view html file
    template_html = 'hmmtuf_compute/schedule_viterbi_compute_view.html'
    template = loader.get_template(template_html)

    db_group_tips = ViterbiSequenceGroupTip.objects.all()
    group_tips = ["None"]

    for item in db_group_tips:
        group_tips.append(item.tip)

    # get the hmms we have
    hmms = HMMModel.objects.all()

    if len(hmms) == 0:
        context = {"error_empty_hmm_list": "HMM models have not been created."}
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    hmm_names = []
    for item in hmms:
        hmm_names.append(item.name)

    # get the regions we have
    regions = RegionModel.objects.all()

    if len(regions) == 0:
        context = {"error_empty_region_list": "Regions have not been created.", }
        template = loader.get_template(template_html)
        return HttpResponse(template.render(context, request))

    region_names = []
    for item in regions:
        region_names.append(item.name)

    context = {"region_names": region_names,
               "hmm_names": hmm_names,
               'window_names': WindowType.get_window_types(),
               "sequence_groups": group_tips}

    if ENABLE_SPADE:
        context.update({"use_spade": True})

    if request.method == 'POST':

        form = forms.ViterbiComputeForm(template_html=template_html,
                                        configuration=INVALID_ITEM,
                                        context=context)

        if form.check(request=request) is not OK:
            return form.response

        task_id = models.ViterbiComputation.compute(data=form.as_map())

        # return the id for the computation
        return redirect('success_schedule_viterbi_computation_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


def view_viterbi_path(request, task_id):
    template_html = 'hmmtuf_compute/viterbi_result_view.html'
    template = loader.get_template(template_html)
    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.ViterbiComputation.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))
    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)
        context = view_viterbi_path_exception_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))


def success_schedule_compare_sequences_compute_view(request, task_id):

    template_html = 'hmmtuf_compute/success_schedule_compare_sequences_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def schedule_compare_sequences_compute_view(request):

    template_html = 'hmmtuf_compute/schedule_compare_sequences_compute_view.html'
    template = loader.get_template(template_html)

    db_sequence_tips = ViterbiSequenceGroupTip.objects.all()
    sequence_tips = []

    for item in db_sequence_tips:
        sequence_tips.append(item.tip)

    context = {"metrics": forms.SequenceComparisonComputeForm.NAMES,
               "sequence_tips": sequence_tips}

    if request.method == 'POST':

        form = forms.SequenceComparisonComputeForm(template_html=template_html,
                                                   context=context, configuration=None)

        if form.check(request=request) is not OK:
            return form.response

        task_id = models.CompareViterbiSequenceComputation.compute(data=form.as_map())

        # return the id for the computation
        return redirect('success_schedule_compare_sequences_compute_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


def view_sequence_comparison(request, task_id):

    template_html = 'hmmtuf_compute/sequence_comparison_view.html'
    template = loader.get_template(template_html)
    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.CompareViterbiSequenceComputation.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))
    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)
        context = view_viterbi_path_exception_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))





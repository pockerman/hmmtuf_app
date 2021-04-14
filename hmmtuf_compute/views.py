from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from compute_engine.src.windows import WindowType
from compute_engine import OK


from hmmtuf import INVALID_TASK_ID, INVALID_ITEM, ENABLE_SPADE
from hmmtuf.celery import celery_app
from hmmtuf_home.models import HMMModel, RegionModel, RegionGroupTipModel, ViterbiSequenceGroupTipModel

from hmmtuf_compute import dash_viewer
from . import models
from . import forms
from . view_helpers import get_result_view_context
from . view_helpers import view_viterbi_path_exception_context
from . view_helpers import handle_success_view, get_kmer_view_result, get_repeats_distances_plot


def success_schedule_group_viterbi_compute_view(request, task_id):

    template_html = 'hmmtuf_compute/success_schedule_group_viterbi_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def success_schedule_group_viterbi_compute_all_view(request, task_id):
    """
    Success view for group Viterbi calculation
    """
    template_html = 'hmmtuf_compute/success_schedule_group_viterbi_compute_all_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def success_schedule_viterbi_compute_view(request, task_id):
    """
    Success redirect after scheduling a Viterbi path computation
    """

    template_html = 'hmmtuf_compute/success_schedule_viterbi_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def success_schedule_kmer_compute_view(request, task_id):
    """
    Success redirect after scheduling a Viterbi path computation
    """

    template_html = 'hmmtuf_compute/success_schedule_kmer_compute_view.html'
    return handle_success_view(request=request,
                               template_html=template_html, task_id=task_id)


def schedule_group_viterbi_compute_view(request):
    """
    Serve the view for scheduling viterbi computations
    for Groups for example compute the Viterbi path
    for chromosome 1
    """
    template_html = 'hmmtuf_compute/schedule_group_viterbi_compute_view.html'
    template = loader.get_template(template_html)

    db_group_tips = ViterbiSequenceGroupTipModel.objects.all()
    sequence_groups = ["None"]

    for item in db_group_tips:
        sequence_groups.append(item.tip)

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
    context = {"hmm_names": hmm_names,
               "group_tips": group_tips, "sequence_groups": sequence_groups}

    if ENABLE_SPADE:
        context.update({"use_spade": True})

    if request.method == 'POST':

        form = forms.GroupViterbiComputeForm(template_html=template_html, context=context)

        result = form.check(request=request)
        if result is not OK:
            return form.response

        kwargs = form.kwargs
        task_id = models.GroupViterbiComputationModel.compute(data=kwargs)

        if kwargs["group_tip"] == 'all':
            return redirect('success_schedule_group_viterbi_compute_all_view', task_id=task_id)

        # return the id for the computation
        return redirect('success_schedule_group_viterbi_compute_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


def view_group_viterbi_all(request, task_id):
    template_html = 'hmmtuf_compute/group_viterbi_result_all_view.html'
    template = loader.get_template(template_html)

    try:
        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.GroupViterbiComputationModel.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))

    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        if task is None:
            return success_schedule_group_viterbi_compute_view(request, task_id=INVALID_TASK_ID)

        context = view_viterbi_path_exception_context(task=task, task_id=task_id,
                                                      model=models.GroupViterbiComputationModel.__name__)
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
        task = models.GroupViterbiComputationModel.objects.get(task_id=task_id)
        context = get_result_view_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))

    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)

        if task is None:
            return success_schedule_group_viterbi_compute_view(request, task_id=INVALID_TASK_ID)

        context = view_viterbi_path_exception_context(task=task, task_id=task_id,
                                                      model=models.GroupViterbiComputationModel.__name__)
        return HttpResponse(template.render(context, request))


def schedule_hmm_viterbi_compute_view(request):
    """
    Schedule a region Viterbi computation.
    """

    # the view html file
    template_html = 'hmmtuf_compute/schedule_viterbi_compute_view.html'
    template = loader.get_template(template_html)

    db_group_tips = ViterbiSequenceGroupTipModel.objects.all().order_by('tip')
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
    regions = RegionModel.objects.all().order_by('chromosome', 'name')

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

        task_id = models.ViterbiComputationModel.compute(data=form.kwargs)

        # return the id for the computation
        return redirect('success_schedule_viterbi_computation_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


def view_viterbi_path(request, task_id):
    """
    Render the computed Viterbi path
    """
    template_html = 'hmmtuf_compute/viterbi_result_view.html'
    template = loader.get_template(template_html)
    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        task = models.ViterbiComputationModel.objects.get(task_id=task_id)
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


def schedule_kmers_calculation_view(request):
    """
    Scedule a kmers calculation
    """

    template_html = "hmmtuf_compute/schedule_kmers_calculation_view.html"
    template = loader.get_template(template_name=template_html)

    context = {}

    if request.method == 'POST':

        form = forms.KmerComputeForm(template_html=template_html,
                                     context=context, configuration=None)

        #if form.check(request=request) is not OK:
        #    return form.response

        # the id of the task
        #task_id = models.CompareViterbiSequenceComputationModel.compute(data=form.kwargs)
        task_id = 0

        # return the id for the computation
        return redirect('success_schedule_kmer_compute_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


def view_repeats_distances_plot(request):
    """
    Serves the view for Dash based view for
    plotting repeats distances
    """
    dash_viewer.repeats_plot_viewer.layout = get_repeats_distances_plot(request=request)
    return redirect(to="/django_plotly_dash/app/repeats_plot_viewer_app/")


def view_kmers(request, task_id):
    """
    Serves the kmers view for the computation identified
    by the task_id
    """

    # set up the Dash viewer layout
    dash_viewer.kmer_viewer.layout = get_kmer_view_result(request=request, task_id=task_id)
    #import dash
    #import dash_core_components as dcc
    #import dash_html_components as html
    #import plotly.express as px
    #from django_plotly_dash import DjangoDash
    #import pandas as pd



    # organize data into a Pandas DF
    #df = pd.DataFrame({
    #    "Kmer": ["AAAA", "TTTT", "ATTA", "GGGG", "AGGG", "ACTG"],
    #    "Amount": [4, 1, 2, 2, 4, 5],
       # "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    #})

    # the figure to dispay
    #fig = px.bar(df, x="Kmer", y="Amount", color="Kmer", barmode="group")

    # set up the layout for the app
    """
    hmmtuf_compute_app_config_with_viewer.kmer_viewer.layout = html.Div(children=[
        html.H1(children='Kmer Viewer', style={"textAlign": "center", "color": '#7FDBFF'}),
        dcc.Graph(
            id='example-graph',
            figure=fig
        )
    ])
    """

    # after building the data for the
    # app redirect to view
    return redirect(to="/django_plotly_dash/app/kmer_viewer_app/")




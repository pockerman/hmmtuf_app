import random
from django.template import loader
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash


from compute_engine.src.utils import get_sequence_name, get_tdf_file
from compute_engine.src.enumeration_types import JobResultEnum, JobType
from compute_engine.src.dash_helpers import create_figure_plot, get_layout

from compute_engine import INFO
from hmmtuf_compute import dash_viewer
from hmmtuf.celery import celery_app
from hmmtuf.helpers import make_bed_path
from hmmtuf.helpers import get_configuration
from hmmtuf import INVALID_TASK_ID

from .models import ViterbiComputationModel, GroupViterbiComputationModel, KmerComputationModel


def get_repeats_distances_plot(request):

    # we also need to add
    # a callback to check on the result
    @dash_viewer.repeats_plot_viewer.callback(Output("error-messages-id", component_property='children'),
                                              Output("normal-bar-chart", "figure"),
                                              Output("normal-n-distances", component_property='children'),
                                              Output("tuf-bar-chart", "figure"),
                                              Output("tuf-n-distances", component_property='children'),
                                              Output("core-bar-chart", "figure"),
                                              Output("core-n-distances", component_property='children'),
                                              [Input("dropdown-sequence", "value"),
                                               Input("dropdown-distance", "value"),
                                               Input("dropdown-gc-limit-type", "value"),
                                               Input("dropdown-gc-limit", "value"),
                                               Input("gc-limit-value", "value"),
                                               Input("compute-btn", "n_clicks")
                                               ])
    def update_bar_chart(seq_type, distance_type, gc_limit_type,
                         gc_limiter, gc_value, btn_clicked):

        print("{0} Calling callback= update_bar_chart... ".format(INFO))
        print("{0} {1} ".format(INFO, dash.callback_context.triggered))

        if len(dash.callback_context.triggered) == 0:
            btn_clicks = 0
        else:

            # get the changes
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            # if the compute bth is in the changes
            # this means we triger a compute
            if 'compute-btn' in changed_id:
                btn_clicks = 1
            else:
                btn_clicks = 0

        print("{0} Button clicks={1}".format(INFO, btn_clicks))
        metric_type_id = distance_type
        sequence_type_id = seq_type
        error_message = ""

        figs_ids = [1, 2, 3]
        figs = []
        for fid in figs_ids:
            error_message, fig, rows = create_figure_plot(state_type_id=fid,
                                                          metric_type_id=metric_type_id,
                                                          sequence_type_id=sequence_type_id,
                                                          gc_limit_type=gc_limit_type,
                                                          gc_limiter=gc_limiter,
                                                          gc_value=gc_value, btn_clicks=btn_clicks)
            figs.append(fig)
            figs.append(rows)

        return error_message, figs[0], figs[1], figs[2], figs[3], figs[4], figs[5],

    return get_layout()

def get_kmer_view_result(request, task_id):
    # return
    # template_html = 'hmmtuf_compute/kmer_result_view.html'
    # template = loader.get_template(template_html)
    try:

        # if the task exists do not ask celery. This means
        # that either the task failed or succeed
        # task = KmerComputationModel.objects.get(task_id=task_id)
        context = {"show_get_results_button": True,
                   "error_message": "This is a test"}  # get_result_view_context(task=task, task_id=task_id)

        if 'error_task_failed' in context:
            # the task failed so
            # Dash view should show this
            layout = html.Div(children=[
                html.H1(children='Kmer Viewer',
                        style={"textAlign": "center", "color": '#7FDBFF'}),
                html.H2(children="Kmer calculation failed",
                        style={"textAlign": "left", "color": 'red'}),
                html.H3(children="Task id: %s" % task_id,
                        style={"textAlign": "left", "color": 'black'}),
                html.H4(children="Error message: %s" % context["error_message"],
                        style={"textAlign": "left", "color": 'black'})])
            return layout
        elif "show_get_results_button" in context:
            # result is not ready yet
            layout = html.Div(children=[html.H1(children='Kmer Viewer',
                                                style={"textAlign": "center", "color": '#7FDBFF'}),
                                        html.H2(children="Kmer calculation pending",
                                                style={"textAlign": "left", "color": 'blue'}),
                                        html.H3(children="Task id: %s" % task_id,
                                                style={"textAlign": "left", "color": 'black'}),
                                        html.Button(children="Check task", id="check_task", n_clicks=0,
                                                    style={"textAlign": "center", "color": 'black'}),
                                        dcc.Input(id="task_id", type="text", value="%s" % task_id),
                                        html.Div(id='task_results'), ])

            # we also need to add
            # a callback to check on the result
            @dash_viewer.kmer_viewer.callback(Output('task_results', 'children'),
                                              Input('check_task', 'n_clicks'),
                                              State('task_id', 'value'), )
            def fetch_results(check_task_button, input_value):
                print(check_task_button)
                print(input_value)
                choice = random.choice([0, 1])
                if choice == 0:
                    msg = 'Task pending'
                else:
                    msg = "Task finished"
                return html.Div(msg)

            return layout

    except ObjectDoesNotExist:

        # try to ask celery
        # check if the computation is ready
        # if yes collect the results
        # otherwise return the html
        task = celery_app.AsyncResult(task_id)
        context = view_viterbi_path_exception_context(task=task, task_id=task_id)
        return HttpResponse(template.render(context, request))


def get_result_view_context(task, task_id):

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
        # this is success
        configuration = get_configuration()
        wga_name = task.wga_seq_filename.split("/")[-1]
        wga_seq_name = get_sequence_name(configuration=configuration, seq=wga_name)
        wga_tdf_file = get_tdf_file(configuration=configuration, seq=wga_name)

        no_wga_name = task.no_wag_seq_filename.split("/")[-1]
        no_wga_seq_name = get_sequence_name(configuration=configuration, seq=no_wga_name)
        no_wga_tdf_file = get_tdf_file(configuration=configuration, seq=no_wga_name)

        if task.computation_type == JobType.VITERBI_GROUP_ALL.name:
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
                       "tdt_bed_url": make_bed_path(task_id=task_id, bed_name="tdt.bed"),
                       "locus": task.chromosome,
                       "start_region_idx": task.start_region_idx,
                       "end_region_idx": task.end_region_idx}
            return context

        if task.computation_type == JobType.GROUP_VITERBI.name:
            context = {'task_status': task.result,
                       "computation": task,
                       "wga_seq_name": wga_seq_name,
                       "no_wga_seq_name": no_wga_seq_name,
                       "wga_tdf_file": wga_tdf_file,
                       "no_wga_tdf_file": no_wga_tdf_file,
                       "normal_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + '/normal.bed'),
                       "tuf_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + '/tuf.bed'),
                       "deletion_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + "/deletion.bed"),
                       "duplication_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + "/duplication.bed"),
                       "gap_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + "/gap.bed"),
                       "repeats_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + "/rep.bed"),
                       "quad_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + "/quad.bed"),
                       "tdt_bed_url": make_bed_path(task_id=task_id, bed_name=task.chromosome + "/tdt.bed"),
                       "locus": task.chromosome,
                       "start_region_idx": task.start_region_idx,
                       "end_region_idx": task.end_region_idx}
            return context

        if task.computation_type == JobType.KMER.name:
            context = {'task_status': task.result,
                       "computation": task,}
            return context

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
                   "tdt_bed_url": make_bed_path(task_id=task_id, bed_name="tdt.bed"),
                   "locus": task.chromosome,
                   "start_region_idx": task.start_region_idx,
                   "end_region_idx": task.end_region_idx}

        return context


def view_viterbi_path_exception_context(task, task_id, model=ViterbiComputationModel.__name__):

    context = {'task_status': task.status}

    if task.status == JobResultEnum.PENDING.name:

        context.update({'show_get_results_button': True,
                        'task_id': task_id})

    elif task.status == JobResultEnum.SUCCESS.name:

        result = task.get()
        if model == ViterbiComputationModel.__name__:
            computation = ViterbiComputationModel.build_from_map(result, save=True)
            context.update({"computation": computation})
        elif model == GroupViterbiComputationModel.__name__:
            computation = GroupViterbiComputationModel.build_from_map(result, save=True)
            context.update({"computation": computation})
        else:
            raise ValueError("Model name: {0} not found".format(INFO, model))
    elif task.status == JobResultEnum.FAILURE.name:

        result = task.get(propagate=False)

        if model == ViterbiComputationModel.__name__:

            data_map = ViterbiComputationModel.get_invalid_map(task=task, result=result)
            computation = ViterbiComputationModel.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id, "computation": computation})

        elif model == GroupViterbiComputationModel.__name__:

            result = task.get(propagate=False)
            data_map = GroupViterbiComputationModel.get_invalid_map(task=task, result=result)
            computation = GroupViterbiComputationModel.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id,
                            "computation": computation})

        else:
            raise ValueError("Model name: {0} not found".format(INFO, model))

    return context


def handle_success_view(request, template_html, task_id, **kwargs):

    template = loader.get_template(template_html)

    context = {"task_id": task_id}
    if task_id == INVALID_TASK_ID:
        error_msg = "Task does not exist"
        context.update({"error_msg": error_msg})

    if kwargs is not None:
        context.update(kwargs)

    return HttpResponse(template.render(context, request))




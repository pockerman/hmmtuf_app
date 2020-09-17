
from compute_engine.utils import get_sequence_name, get_tdf_file
from compute_engine.job import JobResultEnum
from compute_engine import INFO
from hmmtuf.helpers import make_bed_path
from hmmtuf.helpers import get_configuration

from .models import ViterbiComputation, MultiViterbiComputation

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


def view_viterbi_path_exception_context(task, task_id, model=ViterbiComputation.__name__):

    context = {'task_status': task.status}

    if task.status == JobResultEnum.PENDING.name:

        context.update({'show_get_results_button': True,
                        'task_id': task_id})

    elif task.status == JobResultEnum.SUCCESS.name:

        result = task.get()
        if model == ViterbiComputation.__name__:
            computation = ViterbiComputation.build_from_map(result, save=True)
            context.update({"computation": computation})
        elif model == MultiViterbiComputation.__name__:
            computation = MultiViterbiComputation.build_from_map(result, save=True)
            context.update({"computation": computation})
        else:
            raise ValueError("Model name: {0} not found".format(INFO, model))
    elif task.status == JobResultEnum.FAILURE.name:

        result = task.get(propagate=False)

        if model == ViterbiComputation.__name__:

            data_map = ViterbiComputation.get_invalid_map(task=task, result=result)
            computation = ViterbiComputation.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                        "error_message": str(result),
                        'task_id': task_id, "computation": computation})
        elif model == MultiViterbiComputation.__name__:
            result = task.get(propagate=False)
            data_map = MultiViterbiComputation.get_invalid_map(task=task, result=result)
            computation = MultiViterbiComputation.build_from_map(data_map, save=True)
            context.update({'error_task_failed': True,
                            "error_message": str(result),
                            'task_id': task_id,
                            "computation": computation})
        else:
            raise ValueError("Model name: {0} not found".format(INFO, model))

    return context
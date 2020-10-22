import uuid
from celery.decorators import task
from celery.utils.log import get_task_logger

from hmmtuf_home.models import RegionModel

from compute_engine.src.job import Job
from compute_engine.src.create_regions import main as extract_region
from compute_engine.src.job import JobType, JobResultEnum
from compute_engine import DEFAULT_ERROR_EXPLANATION


logger = get_task_logger(__name__)


def serial_task(configuration):

    from .models import ExtractRegionComputation

    db_task = ExtractRegionComputation()
    db_task.task_id = str(uuid.uuid4())
    db_task.computation_type = JobType.EXTRACT_REGION.name
    db_task.error_explanation = DEFAULT_ERROR_EXPLANATION
    db_task.result = JobResultEnum.PENDING.name
    db_task.save()

    try:

        job = Job(idx=None, input=configuration, worker=extract_region, model=db_task)
        job.execute()

        region_model = RegionModel()
        region_model.file_region = configuration["region_name"] + ".txt"
        region_model.name = configuration["region_name"]
        region_model.chromosome = configuration["chromosome"]
        region_model.save()

        db_task.result = JobResultEnum.SUCCESS.name
        db_task.save()
    except Exception as e:
        db_task.error_explanation = str(e)
        db_task.result = JobResultEnum.FAILURE.name
        db_task.save()

    return db_task.task_id


@task(name="extract_region_task")
def extract_region_task(region_name, chromosome,
                        region_start, region_end,
                        region_path, mark_for_gap_windows,
                        remove_windows_with_gaps,
                        window_size, processing,
                        reference_file, no_wga_file,
                        wga_file, max_depth,
                        ignore_orphans, truncate,
                        quality_threshold, add_indels):

    from .models import ExtractRegionComputation

    task_id = extract_region_task.request.id
    task_id = task_id.replace('-', '_')

    db_task = ExtractRegionComputation()
    db_task.task_id = task_id
    db_task.computation_type = JobType.EXTRACT_REGION.name
    db_task.error_explanation = DEFAULT_ERROR_EXPLANATION
    db_task.result = JobResultEnum.PENDING.name
    db_task.save()

    try:

        configuration = {'processing': {"type": processing}}

        configuration["window_size"] = window_size
        configuration["chromosome"] = chromosome
        configuration["remove_windows_with_gaps"] = remove_windows_with_gaps
        configuration["mark_for_gap_windows"] = mark_for_gap_windows
        configuration["regions"] = {"start": [region_start],
                                    "end": [region_end]}

        configuration["reference_file"] = {"filename": reference_file}
        configuration["no_wga_file"] = {"filename": no_wga_file}
        configuration["wga_file"] = {"filename": wga_file}
        configuration["region_name"] = region_name
        configuration["region_path"] = region_path

        configuration["sam_read_config"] = {"max_depth": max_depth,
                                            "ignore_orphans": ignore_orphans,
                                            "truncate": truncate,
                                            "quality_threshold": quality_threshold,
                                            "add_indels": add_indels}

        extract_region(configuration=configuration)

        region_model = RegionModel()
        region_model.file_region = "my_region.txt"
        region_model.name = region_name
        region_model.chromosome = chromosome
        region_model.save()

        db_task.result = JobResultEnum.SUCCESS.name
        db_task.save()
    except Exception as e:
        db_task.error_explanation = str(e)
        db_task.result = JobResultEnum.FAILURE.name
        db_task.save()



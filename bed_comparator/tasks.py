import os
from celery.decorators import task
from celery.utils.log import get_task_logger
from pathlib import Path

from .task_utils import compute_bed_comparison


@task(name="compute_bed_comparison_task")
def compute_bed_comparison_task():
    task_id = compute_bed_comparison_task.request.id
    return compute_bed_comparison(task_id=task_id)


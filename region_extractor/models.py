from django.db import models

from hmmtuf.config import USE_CELERY
from hmmtuf_home.models import ComputationModel
from .tasks import extract_region_task
from .tasks import serial_task

# Create your models here.

class ExtractRegionComputationModel(ComputationModel):

    class Meta(ComputationModel.Meta):
        db_table = 'extract_region_computation_model'

    @staticmethod
    def compute(data):

        if USE_CELERY:
            # schedule the computation
            task = extract_region_task.delay(region_name=data["region_name"],
                                             chromosome=data["chromosome"],
                                             region_start=data["regions"]["start"],
                                             region_end=data["regions"]["end"],
                                             region_path=data["region_path"],
                                             mark_for_gap_windows=data["mark_for_gap_windows"],
                                             remove_windows_with_gaps=data["remove_windows_with_gaps"],
                                             window_size=data["window_size"],
                                             processing=data["processing"]["type"],
                                             reference_file=data["reference_file"],
                                             no_wga_file=data["no_wga_file"],
                                             wga_file=data["wga_file"],
                                             max_depth=data["sam_read_config"]["max_depth"],
                                             ignore_orphans=data["sam_read_config"]["ignore_orphans"],
                                             truncate=data["sam_read_config"]["truncate"],
                                             quality_threshold=data["sam_read_config"]["quality_threshold"],
                                             add_indels=data["sam_read_config"]["add_indels"])
            return task.id.replace('-', '_')
        else:

            #import pdb
            #pdb.set_trace()
            task_id = serial_task(configuration=data)
            return task_id.replace('-', '_')



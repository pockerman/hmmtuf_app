from celery.decorators import task
from celery.utils.log import get_task_logger

#from .create_regions import main
from hmmtuf_home.models import RegionModel

from compute_engine.create_regions import main


logger = get_task_logger(__name__)


@task(name="extract_region_task")
def extract_region_task(region_name, chromosome, region_start,
                        region_end, processing):

    task_id = extract_region_task.request.id
    task_id = task_id.replace('-', '_')

    #main(configuration=args)

    print("Saving region with name ", region_name)

    configuration = {'processing': 'processing',
                       'chromosome': chromosome,
                       'region_start': region_start,
                       'region_end': region_end}
    main(configuration=configuration)

    region_model = RegionModel()
    region_model.file_region = "my_region.txt"
    region_model.name = region_name
    region_model.chromosome = chromosome
    region_model.save()


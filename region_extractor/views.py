
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from hmmtuf.settings import BASE_DIR
from hmmtuf_home.utils import read_json
from file_loader.models import RegionModel

from .utils import extract_file_names
from .forms import ExtractRegionForm
from .tasks import extract_region_task

# Create your views here.

def extract_region_success_view(request, task_id):
    template = loader.get_template('region_extractor/extract_region_success_view.html')
    context = {"task_id": task_id}
    return HttpResponse(template.render(context, request))


def extract_region_view(request):

    # read the files
    config_file = '%s/config.json' % BASE_DIR
    configuration = read_json(filename=config_file)
    reference_files_names, wga_files_names, nwga_files_names = extract_file_names(configuration=configuration)
    template = loader.get_template('region_extractor/extract_region_view.html')

    context = {"outlier_remove_names": ["None", "Mean Cutoff"],
               "reference_files": reference_files_names,
               "wga_files": wga_files_names,
               "nwga_files": nwga_files_names}

    if request.method == 'POST':

        # check if there are any errors
        # if not submit the task and redirect to success
        form = ExtractRegionForm(request=request)
        #import pdb
        #pdb.set_trace()
        result = ExtractRegionForm.extract(form)


        if result is not True:
            context.update({"has_errors": True, "errors": result})
            return HttpResponse(template.render(context, request))

        try:
            model = RegionModel.objects.get(name=form.region_name)
            context.update({"has_errors": True, "errors": "Region with name: {0} already exists".format(form.region_name)})
            return HttpResponse(template.render(context, request))
        except ObjectDoesNotExist:

            task = extract_region_task.delay(region_name=form.region_name,
                                             chromosome=form.chromosome,
                                             region_start=form.region_start,
                                             region_end=form.region_end,
                                             processing=form.processing)

            # return the id for the computation
            return redirect('extract_region_success_view', task_id=task.id)

        """
        
        else:
            print("Ref file: ", form.ref_file)
            print("WGA file: ", form.wga_ref_seq_file)
            print("No-WGA file: ", form.nwga_ref_seq_file)

            print("Quality threshold:", form.quality_threshold)
            print("Indels: ", form.add_indels)
            print("Truncate: ", form.truncate)
            print("Ignore orphans:", form.ignore_orphans)
            print("Max depth: ",form.max_depth)
            print("Outlier remove:", form.outlier_remove)
            print("Chromosome: ", form.chromosome)
            print("Window size: ", form.window_size)
            print("Region end: ", form.region_end)
            print("Region start:", form.region_start)
        """

    return HttpResponse(template.render(context, request))


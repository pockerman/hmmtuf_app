from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from compute_engine.src.utils import extract_file_names

from hmmtuf.settings import REGIONS_FILES_ROOT
from webapp_utils.helpers import get_configuration
from hmmtuf_home.models import RegionModel

from .forms import ExtractRegionForm
from .models import ExtractRegionComputationModel


# Create your views here.

def extract_region_success_view(request, task_id):
    template = loader.get_template('region_extractor/extract_region_success_view.html')
    context = {"task_id": task_id}
    return HttpResponse(template.render(context, request))


def extract_region_view(request):

    configuration = get_configuration()
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

                configuration = {'processing': {"type": "serial"}}

                configuration["window_size"] = form.window_size
                configuration["chromosome"] = form.chromosome
                configuration["remove_windows_with_gaps"] = form.remove_gap_windows
                configuration["mark_for_gap_windows"] = form.mark_for_gap_windows
                configuration["regions"] = {"start": [form.region_start],
                                            "end": [form.region_end]}

                configuration["reference_file"] = {"filename": form.ref_file}
                configuration["no_wga_file"] = {"filename": form.nwga_ref_seq_file}
                configuration["wga_file"] = {"filename": form.wga_ref_seq_file}
                configuration["region_name"] = form.region_name
                configuration["region_path"] = REGIONS_FILES_ROOT

                configuration["sam_read_config"] = {"max_depth": form.max_depth,
                                                    "ignore_orphans": form.ignore_orphans,
                                                    "truncate": form.truncate,
                                                    "quality_threshold": form.quality_threshold,
                                                    "add_indels": form.add_indels}

                task_id = ExtractRegionComputationModel.compute(data=configuration)

                # return the id for the computation
                return redirect('extract_region_success_view', task_id=task_id)

    return HttpResponse(template.render(context, request))


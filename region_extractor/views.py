
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

from hmmtuf.settings import BASE_DIR
from hmmtuf_home.utils import read_json

from .utils import extract_file_names
from .forms import ExtractRegionForm

# Create your views here.


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

        form = ExtractRegionForm(request=request)
        result = ExtractRegionForm.extract(form)

        if result is not True:
            context.update({"error": result})
            return HttpResponse(template.render(context, request))
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



    return HttpResponse(template.render(context, request))


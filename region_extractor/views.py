
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

from hmmtuf.settings import BASE_DIR
from hmmtuf_home.utils import read_json

# Create your views here.


def extract_region_view(request):

    # read the files
    config_file = '%s/config.json' % BASE_DIR
    configuration = read_json(filename=config_file)

    reference_files_names = []
    ref_files = configuration["sequence_files"]["reference_files"]

    for i in range(len(ref_files)):
        files = configuration["sequence_files"]["reference_files"][i]

        for f in files:
            reference_files_names.extend(files[f])

    wga_files_names = []
    wga_files = configuration["sequence_files"]["wga_files"]

    for i in range(len(wga_files)):
        files = configuration["sequence_files"]["wga_files"][i]

        for f in files:
            wga_files_names.extend(files[f])

    nwga_files_names = []
    nwga_files = configuration["sequence_files"]["no_wga_files"]

    for i in range(len(nwga_files)):
        files = configuration["sequence_files"]["no_wga_files"][i]

        for f in files:
            nwga_files_names.extend(files[f])

    template = loader.get_template('region_extractor/extract_region_view.html')
    context = {"outlier_remove_names": ["None", "Mean Cutoff"],
               "reference_files":reference_files_names,
               "wga_files": wga_files_names,
               "nwga_files": nwga_files_names}
    return HttpResponse(template.render(context, request))


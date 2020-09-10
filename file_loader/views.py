from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage

from hmmtuf.settings import REGIONS_FILES_ROOT
from hmmtuf.settings import HMM_FILES_ROOT
from hmmtuf.settings import BASE_DIR
from hmmtuf_home.models import HMMModel, RegionModel
from compute_engine.utils import read_json, extract_file_names
from compute_engine import OK
from .forms import ErrorHandler, RegionLoadForm


__all__ = ['load_hmm_json_view', 'load_region_view']


# Views

def success_load_view_hmm(request, hmm_name):
    template = loader.get_template('file_loader/load_success.html')
    return HttpResponse(template.render({'name': hmm_name, 'load_hmm': True}, request))


def success_load_view_region(request, region_name):
    template = loader.get_template('file_loader/load_success.html')
    return HttpResponse(template.render({'name': region_name, 'load_region':True}, request))


def load_hmm_json_view(request):
    """
    The view for loading a JSON file describing
    an HMM
    """

    if request.method == 'POST':

        error_handler = ErrorHandler(filename="hmm_filename", item_name="hmm_name",
                                     error_sponse_msg={"error_missing_file": "Missing HMM filename",
                                                       "error_missing_name": "Missing HMM name"},
                                     template_html='file_loader/load_hmm_view.html')

        if error_handler.check(request=request) is not OK:
             return error_handler.response

        # check if the HMM model with such a name exists
        # if yes then we return an error
        try:
            model = HMMModel.objects.get(name=error_handler.name)
        except ObjectDoesNotExist:

            # the object does not exist we can save the file
            file_loaded = error_handler.file_loaded
            fs = FileSystemStorage(HMM_FILES_ROOT)
            file_loaded_name = error_handler.name + '.json'
            filename = fs.save(file_loaded_name, file_loaded)

            hmm_inst = HMMModel()
            hmm_inst.file_hmm = HMM_FILES_ROOT + file_loaded_name
            hmm_inst.name = error_handler.name
            hmm_inst.extension = 'json'
            hmm_inst.save()

            return redirect('success_load_view_hmm', hmm_name=file_loaded.name)

        template = loader.get_template('file_loader/load_hmm_view.html')
        return HttpResponse(template.render({"error_name_exist": "The HMM name exists"}, request))

    template = loader.get_template('file_loader/load_hmm_view.html')
    return HttpResponse(template.render({}, request))


def load_region_view(request):
    """
    The view for loading a JSON file describing
    an HMM
    """

    if request.method == 'POST':

        error_handler = RegionLoadForm(filename="region_file", item_name="region_name",
                                       error_sponse_msg={"error_missing_file": "Missing Region filename",
                                                       "error_missing_name": "Missing Region name"},
                                       template_html='file_loader/load_region_view.html')

        if error_handler.check(request=request) is not OK:
            return error_handler.response

            # check if the HMM model with such a name exists
            # if yes then we return an error
        try:
            model = RegionModel.objects.get(name=error_handler.name)
        except ObjectDoesNotExist:

            # the object does not exist we can save the file
            file_loaded = error_handler.file_loaded
            fs = FileSystemStorage(REGIONS_FILES_ROOT)

            file_loaded_name = error_handler.name + '.txt'
            filename = fs.save(file_loaded_name, file_loaded)

            region_inst = RegionModel()

            region_inst.name = error_handler.name
            region_inst.file_region = REGIONS_FILES_ROOT + file_loaded_name
            region_inst.name = error_handler.name
            region_inst.extension = 'txt'
            region_inst.chromosome = error_handler.chromosome
            region_inst.ref_seq_file = error_handler.ref_seq_region
            region_inst.wga_seq_file = error_handler.wga_seq_region
            region_inst.no_wga_seq_file = error_handler.no_wga_seq_region
            region_inst.save()

            return redirect('success_load_view_region', region_name=file_loaded.name)

        template = loader.get_template('file_loader/load_region_view.html')
        return HttpResponse(template.render({"error_name_exist": "The region name exists. Specify "
                                                                 "another name for the region"}, request))

    configuration = read_json(filename="%s/config.json" % BASE_DIR)

    reference_files_names, wga_files_names, nwga_files_names = extract_file_names(configuration=configuration)
    context = {"reference_files": reference_files_names,
               "wga_files": wga_files_names,
               "nwga_files": nwga_files_names}

    # if not post simply return the view
    template = loader.get_template('file_loader/load_region_view.html')
    return HttpResponse(template.render(context, request))


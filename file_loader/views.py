from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist

from django.core.files.storage import FileSystemStorage
from hmmtuf.settings import REGIONS_FILES_ROOT
from hmmtuf.settings import REGIONS_FILES_URL
from hmmtuf.settings import HMM_FILES_ROOT
from hmmtuf.settings import HMM_FILES_URL
from .forms import ErrorHandler, OK
from .models import HMMModel, RegionModel

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
             return error_handler.response()

        # check if the HMM model with such a name exists
        # if yes then we return an error
        try:
            model = HMMModel.objects.get(name=error_handler.get_name())
        except ObjectDoesNotExist:

            # the object does not exist we can save the file
            file_loaded = error_handler.get_file_loaded()
            fs = FileSystemStorage(HMM_FILES_ROOT)
            filename = fs.save(file_loaded.name, file_loaded)

            hmm_inst = HMMModel()
            hmm_inst.filename = file_loaded.name
            hmm_inst.name = error_handler.get_name()
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

        error_handler = ErrorHandler(filename="region_file", item_name="region_name",
                                     error_sponse_msg={"error_missing_file": "Missing Region filename",
                                                       "error_missing_name": "Missing Region name"},
                                     template_html='file_loader/load_region_view.html')

        if error_handler.check(request=request) is not OK:
            return error_handler.response()

            # check if the HMM model with such a name exists
            # if yes then we return an error
        try:
            model = RegionModel.objects.get(name=error_handler.get_name())
        except ObjectDoesNotExist:

            # the object does not exist we can save the file
            file_loaded = error_handler.get_file_loaded()
            fs = FileSystemStorage(REGIONS_FILES_ROOT)
            filename = fs.save(file_loaded.name, file_loaded)

            region_inst = RegionModel()
            region_inst.filename = file_loaded.name
            region_inst.name = error_handler.get_name()
            region_inst.extension = 'txt'
            region_inst.save()

            return redirect('success_load_view_region', region_name=file_loaded.name)

        template = loader.get_template('file_loader/load_region_view.html')
        return HttpResponse(template.render({"error_name_exist": "The region name exists. Specify "
                                                                 "another name for the region"}, request))

    # if not post simply return the view
    template = loader.get_template('file_loader/load_region_view.html')
    return HttpResponse(template.render({}, request))


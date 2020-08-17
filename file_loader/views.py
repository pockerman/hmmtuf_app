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
from .models import HMMModel

__all__ = ['load_hmm_json_view', 'load_region_view']


# Views

def success_load_view_hmm(request, hmm_name):
    template = loader.get_template('file_loader/load_success.html')
    return HttpResponse(template.render({'name': hmm_name}, request))


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

        file_loaded = error_handler.get_file_loaded()
        fs = FileSystemStorage(HMM_FILES_ROOT)
        filename = fs.save(file_loaded.name, file_loaded)
        uploaded_file_url = fs.url(HMM_FILES_URL + filename)


        hmm_inst = HMMModel()
        hmm_inst.filename = file_loaded.name
        hmm_inst.name = error_handler.get_name()
        hmm_inst.extension = 'json'

        #models = HMMModel.objects.all() #get(name=hmm_inst.name)
        #print(type(models))
        #print(len(models))

        try:
            model = HMMModel.objects.get(name=hmm_inst.name)
        except ObjectDoesNotExist:
            hmm_inst.save()
            return redirect('success_load_view_hmm', hmm_name=hmm_inst.name)

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

        error_handler = ErrorHandler(filename="regionFile", item_name="regionName",
                                     error_sponse_msg={"error_missing_file": "Missing Region filename",
                                                       "error_missing_name": "Missing Region name"},
                                     template_html='file_loader/load_region_view.html')

        if error_handler.check(request=request) is not OK:
            return error_handler.response()

        file_loaded = error_handler.get_file_loaded()

        fs = FileSystemStorage(REGIONS_FILES_ROOT)
        filename = fs.save(file_loaded.name, file_loaded)
        uploaded_file_url = fs.url(REGIONS_FILES_URL + filename)

        template = loader.get_template('file_loader/load_region_view.html')
        return HttpResponse(template.render({"uploaded_file_url": uploaded_file_url}, request))

    # if not post simply return the view
    template = loader.get_template('file_loader/load_region_view.html')
    return HttpResponse(template.render({}, request))


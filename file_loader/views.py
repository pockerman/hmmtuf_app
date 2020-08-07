from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.core.files.storage import FileSystemStorage

# Views

def load_hmm_json_view(request):
    """
    The view for loading a JSON file describing
    an HMM
    """

    if request.method == 'POST':
        print("Request is POST")

    template = loader.get_template('file_loader/load_hmm_view.html')
    return HttpResponse(template.render({}, request))

def load_region_view(request):
    """
    The view for loading a JSON file describing
    an HMM
    """

    if request.method == 'POST':

        region_file = request.FILES.get("regionFile", None)

        if region_file is None:
            template = loader.get_template('file_loader/load_region_view.html')
            return HttpResponse(template.render({"error_missing_file": "Region file is not specified"}, request))

        region_name = request.POST.get("regionName", '')

        if region_name  == '':
            print("Region name is None")
            template = loader.get_template('file_loader/load_region_view.html')
            return HttpResponse(template.render({"error_missing_region_name": "Region name is not specified"}, request))
        else:
            print("Region name is: ", region_name)

        region_file = request.FILES["regionFile"]
        fs = FileSystemStorage()
        filename = fs.save(region_file.name, region_file)
        uploaded_file_url = fs.url(filename)
        print("Request is POST")

        template = loader.get_template('file_loader/load_region_view.html')
        return HttpResponse(template.render({"uploaded_file_url": uploaded_file_url}, request))

    # if not post simply return the view
    template = loader.get_template('file_loader/load_region_view.html')
    return HttpResponse(template.render({}, request))


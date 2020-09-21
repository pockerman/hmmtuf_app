import os
import shutil

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib import messages

from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT


# Create your views here.
def home_view(request):
    template_html = 'hmmtuf_home/index.html'
    template = loader.get_template(template_html)
    return HttpResponse(template.render({}, request))


def delete_task_directories_view(request):

    template_html = 'hmmtuf_home/delete_task_directories_view.html'
    context = {}
    if request.method == 'POST':

        directories = os.listdir(path=VITERBI_PATHS_FILES_ROOT)

        counter = 0
        for name in directories:

            try:
                if os.path.isdir(VITERBI_PATHS_FILES_ROOT + name):
                    shutil.rmtree(os.path.join(VITERBI_PATHS_FILES_ROOT, name))
                    counter += 1
            except Exception as e:
                messages.error(request, "Attempt to remove task "
                                        "directory {0} failed".format(VITERBI_PATHS_FILES_ROOT + name))
                return redirect("index")

        if counter == 0:
            messages.info(request, "No directories to remove".format(counter))
        else:
            messages.info(request, "Successfully removed {0} directories".format(counter))
        return redirect("index")

    template = loader.get_template(template_html)
    return HttpResponse(template.render(context, request))



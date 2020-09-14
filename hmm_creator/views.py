from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist

from django.core.files.storage import FileSystemStorage
from hmmtuf.settings import REGIONS_FILES_ROOT
from hmmtuf.settings import HMM_FILES_ROOT


def create_hmm_view(request):

    if request.method == 'POST':
        print("Iam posting....")

    template = loader.get_template('hmm_creator/create_hmm_view.html')
    return HttpResponse(template.render({}, request))


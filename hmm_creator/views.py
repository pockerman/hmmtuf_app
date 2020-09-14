from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist

from django.core.files.storage import FileSystemStorage
from hmmtuf.settings import REGIONS_FILES_ROOT
from hmmtuf.settings import HMM_FILES_ROOT

from .forms import HMMFormCreator

def create_hmm_view(request):

    context = {}
    if request.method == 'POST':

        form = HMMFormCreator(template='hmm_creator/create_hmm_view.html',
                              context=context)

        result = form.check(request=request)

        print("Iam posting....")

    template = loader.get_template('hmm_creator/create_hmm_view.html')
    return HttpResponse(template.render(context, request))


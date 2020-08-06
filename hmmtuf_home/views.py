from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def home_view(request):
    template = loader.get_template('hmmtuf_home/index.html')
    return HttpResponse(template.render({}, request))

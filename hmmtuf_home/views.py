from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

from hmmtuf.settings import BASE_DIR
from compute_engine.utils import OK, read_json, extract_file_names
from compute_engine.utils import extract_path

# Create your views here.
def home_view(request):
    template = loader.get_template('hmmtuf_home/index.html')
    return HttpResponse(template.render({}, request))


def sequence_view_request_view(request):
    template = loader.get_template('hmmtuf_home/sequence_view_request_view.html')

    configuration = read_json(filename="%s/config.json" % BASE_DIR)

    reference_files_names, wga_files_names, nwga_files_names = extract_file_names(configuration=configuration)
    context = {"reference_files": reference_files_names,
               "wga_files": wga_files_names,
               "nwga_files": nwga_files_names}

    if request.method == 'POST':
        ref_seq = request.POST.get('ref_seq_region', None)
        wga_seq = request.POST.get('wga_seq_region', None)
        no_wga_seq = request.POST.get('no_wga_seq_region', None)
        return redirect('sequence_view', ref_seq=ref_seq,
                        wga_seq=wga_seq, no_wga_seq=no_wga_seq)
    return HttpResponse(template.render(context, request))


def sequence_view(request, ref_seq, wga_seq, no_wga_seq):
    template = loader.get_template('hmmtuf_home/sequence_view.html')
    configuration = read_json(filename="%s/config.json" % BASE_DIR)
    path = extract_path(configuration=configuration, ref_file=ref_seq)

    return HttpResponse(template.render({'ref_seq_file': path + ref_seq,
                                         'ref_seq_file_index': path + ref_seq + '.fai',
                                         'wga_seq': path + wga_seq,
                                         'wga_seq_index': path + wga_seq + '.bai',
                                         'no_wga_seq': path + no_wga_seq,
                                         'no_wga_seq': path + no_wga_seq + '.bai'}, request))



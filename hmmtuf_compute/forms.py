from django.http import HttpResponse
from django.template import loader

from compute_engine.utils import read_json, extract_file_names, extract_path
from compute_engine import OK

from hmmtuf import VITERBI_PATH_FILENAME
from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf_home.models import HMMModel, RegionModel


class MultipleViterbiComputeForm(object):

    def __init__(self, template_html, configuration, context):
        self._response = None
        self._chromosome = None
        self._ref_sequence_file = None
        self._hmm_name = None
        self._template_html = template_html
        self._context = context
        self._configuration = configuration
        self._path = None
        self._group_tip = None

    @property
    def response(self):
        return self._response

    def as_map(self):
        return {"chromosome": self._chromosome,
                "hmm_name": self._hmm_name,
                "ref_seq_file": self._ref_sequence_file,
                "path": self._path,
                "group_tip": self._group_tip}

    def check(self, request):

        self._ref_sequence_file = request.POST.get("reference_files_names", "")
        if self._ref_sequence_file == "":
            template = loader.get_template(self._template_html)
            self._context.update({"error_found": "No reference sequence file specified"})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK

        # do we have regions for this
        self._hmm_name = request.POST.get("hmm", "")
        if self._hmm_name == "":
            return not OK

        self._chromosome = request.POST.get("chromosome", "")
        if self._chromosome == "":
            template = loader.get_template(self._template_html)
            self._context.update({"error_found": "No  chromosome specified"})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK

        # do we have region files for this
        # reference file and chromosome
        self._path = extract_path(configuration=self._configuration,
                                  ref_file=self._ref_sequence_file)

        self._group_tip = request.POST.get("group_tip")

        #file_ = self._path + self._ref_sequence_file
        objects = RegionModel.objects.filter(group_tip__tip=self._group_tip,
                                             chromosome=self._chromosome)

        if len(objects) == 0:
            template = loader.get_template(self._template_html)
            self._context.update({"error_found": True,
                                  "no_seq_chromosome": "No regions for chromosome {0}\
             and group {1}".format(self._chromosome, self._group_tip )})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK

        return OK


def wrap_data_for_viterbi_calculation(request):

    # find the HMM
    hmm_name = request.POST.get("hmm", '')
    hmm_model = HMMModel.objects.get(name=hmm_name)
    hmm_filename = hmm_model.file_hmm.name

    region_name = request.POST.get("region", '')
    region = RegionModel.objects.get(name=region_name)
    region_filename = region.file_region.name

    ref_seq_file = region.ref_seq_file
    wga_seq_file = region.wga_seq_file
    no_wag_seq_file = region.no_wga_seq_file

    window_type = 'BOTH'
    chromosome = request.POST.get('chromosome', '')
    sequence_size = request.POST.get('sequence_size', '')
    n_sequences = request.POST.get('n_sequences', '')

    if n_sequences == '':
        pass
    else:
        n_sequences = int(n_sequences)

    if sequence_size == '':
        sequence_size = None
    else:
        sequence_size = int(sequence_size)

    kwargs = {'hmm_name': hmm_name,
              'region_name': region_name,
              'chromosome': chromosome,
              'window_type': window_type,
              'viterbi_path_files_root': VITERBI_PATHS_FILES_ROOT,
              'viterbi_path_filename':  VITERBI_PATH_FILENAME,
              'region_filename': region_filename,
              'hmm_filename': hmm_filename,
              'sequence_size': sequence_size,
              'n_sequences': n_sequences,
              'path_img': VITERBI_PATHS_FILES_ROOT,
              'ref_seq_file': ref_seq_file,
              'wga_seq_file': wga_seq_file,
              'no_wag_seq_file': no_wag_seq_file}

    return kwargs
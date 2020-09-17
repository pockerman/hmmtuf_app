from django.http import HttpResponse
from django.template import loader

from compute_engine.utils import read_json, extract_file_names, extract_path
from compute_engine import OK

from hmmtuf import VITERBI_PATH_FILENAME
from hmmtuf import INVALID_ITEM
from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf_home.models import HMMModel, RegionModel


class GroupViterbiComputeForm(object):

    def __init__(self, template_html, context):

        self._template_html = template_html
        self._context = context
        self._response = INVALID_ITEM
        self._group_tip = INVALID_ITEM
        self._hmm_name = INVALID_ITEM

    @property
    def response(self):
        return self._response

    def as_map(self):
        return {"hmm_name": self._hmm_name,
                "group_tip": self._group_tip}

    def check(self, request):

        # do we have regions for this
        self._hmm_name = request.POST.get("hmm", "")
        if self._hmm_name == "":
            return not OK

        self._group_tip = request.POST.get("group_tip")
        objects = RegionModel.objects.filter(group_tip__tip=self._group_tip)

        if len(objects) == 0:
            template = loader.get_template(self._template_html)
            self._context.update({"error_found": True,
                                  "no_seq_chromosome": "No regions for group {0}".format(self._group_tip )})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK

        return OK


class MultipleViterbiComputeForm(object):

    def __init__(self, template_html, configuration, context):

        self._template_html = template_html
        self._context = context
        self._configuration = configuration
        self._path = INVALID_ITEM
        self._group_tip = INVALID_ITEM
        self._response = INVALID_ITEM
        self._chromosome = INVALID_ITEM
        self._ref_sequence_file = INVALID_ITEM
        self._wga_seq_filename = INVALID_ITEM
        self._no_wga_seq_filename = INVALID_ITEM
        self._hmm_name = INVALID_ITEM

    @property
    def response(self):
        return self._response

    def as_map(self):
        return {"chromosome": self._chromosome,
                "hmm_name": self._hmm_name,
                "ref_seq_filename": self._ref_sequence_file,
                "wga_seq_filename": self._wga_seq_filename,
                "no_wga_seq_filename": self._no_wga_seq_filename,
                "path": self._path,
                "group_tip": self._group_tip,
                }

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
        objects = RegionModel.objects.filter(group_tip__tip=self._group_tip,
                                             chromosome=self._chromosome)

        if len(objects) == 0:
            template = loader.get_template(self._template_html)
            self._context.update({"error_found": True,
                                  "no_seq_chromosome": "No regions for chromosome {0}\
             and group {1}".format(self._chromosome, self._group_tip )})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK

        region = objects[0]
        self._wga_seq_filename = region.wga_seq_file
        self._no_wga_seq_filename = region.no_wga_seq_file
        self._ref_sequence_file = region.ref_seq_file
        return OK


class ViterbiComputeForm(object):

    def __init__(self, template_html, configuration, context):
        self._template_html = template_html
        self._configuration = configuration
        self._context = context

        self._kwargs = {'hmm_name': INVALID_ITEM,
                        'region_name': INVALID_ITEM,
                          'chromosome': INVALID_ITEM,
                          'window_type': INVALID_ITEM,
                          'region_filename': INVALID_ITEM,
                          'hmm_filename': INVALID_ITEM,
                          'sequence_size': INVALID_ITEM,
                          'n_sequences': INVALID_ITEM,
                          'ref_seq_file': INVALID_ITEM,
                          'wga_seq_file': INVALID_ITEM,
                          'no_wag_seq_file': INVALID_ITEM,
                          'chromosome_index': INVALID_ITEM,
                          "remove_dirs": INVALID_ITEM,
                          "use_spade": INVALID_ITEM}

    def as_map(self):
        return self._kwargs

    def check(self, request):

        # find the HMM
        hmm_name = request.POST.get("hmm", '')
        hmm_model = HMMModel.objects.get(name=hmm_name)
        hmm_filename = hmm_model.file_hmm.name

        checkbox = request.POST.get('remove_dirs', False)

        if checkbox == 'True':
            checkbox = True

        use_spade = request.POST.get('use_spade', False)

        if use_spade == 'True':
            use_spade = True

        region_name = request.POST.get("region", '')
        region = RegionModel.objects.get(name=region_name)

        region_filename = region.file_region.name
        ref_seq_file = region.ref_seq_file
        chromosome = region.chromosome

        wga_seq_file = region.wga_seq_file
        no_wag_seq_file = region.no_wga_seq_file

        window_type = 'BOTH'
        n_sequences = 1

        self._kwargs = {'hmm_name': hmm_name,
                      'region_name': region_name,
                      'chromosome': chromosome,
                      'window_type': window_type,
                      'viterbi_path_files_root': VITERBI_PATHS_FILES_ROOT,
                      'viterbi_path_filename':  VITERBI_PATH_FILENAME,
                      'region_filename': region_filename,
                      'hmm_filename': hmm_filename,
                      'sequence_size': INVALID_ITEM,
                      'n_sequences': n_sequences,
                      'path_img': VITERBI_PATHS_FILES_ROOT,
                      'ref_seq_file': ref_seq_file,
                      'wga_seq_file': wga_seq_file,
                      'no_wag_seq_file': no_wag_seq_file,
                      "chromosome_index": region.chromosome_index,
                      "remove_dirs": checkbox,
                      "use_spade": use_spade}


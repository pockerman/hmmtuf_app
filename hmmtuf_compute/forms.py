from abc import abstractmethod
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist

from compute_engine.utils import extract_path
from compute_engine.string_sequence_calculator import TextDistanceCalculator
from compute_engine import OK

from hmmtuf import VITERBI_PATH_FILENAME
from hmmtuf import INVALID_ITEM
from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf_home.models import HMMModel, RegionModel, ViterbiSequenceModel, ViterbiSequenceGroupTip


class ComputeFormBase(object):

    def __init__(self, template_html, context, configuration):
        self._template_html = template_html
        self._context = context
        self._configuration = configuration
        self._response = INVALID_ITEM

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    @property
    def context(self):
        return self._context

    @property
    def template_html(self):
        return self._template_html

    @abstractmethod
    def as_map(self):
        pass

    @abstractmethod
    def check(self, request):
        pass


class GroupViterbiComputeForm(ComputeFormBase):

    def __init__(self, template_html, context):
        super(GroupViterbiComputeForm, self).__init__(template_html=template_html,
                                                      context=context, configuration=None)

        self._group_tip = INVALID_ITEM
        self._hmm_name = INVALID_ITEM
        self._remove_dirs = INVALID_ITEM
        self._use_spade = INVALID_ITEM
        self._sequence_group = INVALID_ITEM
        self._scheduler_id = INVALID_ITEM

    def as_map(self):
        return {"hmm_name": self._hmm_name,
                "group_tip": self._group_tip,
                "remove_dirs": self._remove_dirs,
                "use_spade": self._use_spade,
                "sequence_group": self._sequence_group,
                "scheduler_id": self._scheduler_id}

    def check(self, request):

        self._hmm_name = request.POST.get("hmm", "")
        if self._hmm_name == "":
            return not OK

        self._group_tip = request.POST.get("group_tip")

        if self._group_tip != "all":

            objects = RegionModel.objects.filter(group_tip__tip=self._group_tip)

            if len(objects) == 0:
                template = loader.get_template(self._template_html)
                self.context.update({"error_found": True,
                                      "no_seq_chromosome": "No regions for group {0}".format(self._group_tip)})

                self.response = HttpResponse(template.render(self.context, request))
                return not OK

        self._remove_dirs = request.POST.get('remove_dirs', False)
        if self._remove_dirs == 'True':
            self._remove_dirs = True

        self._use_spade = request.POST.get('use_spade', False)
        if self._use_spade == 'True':
            self._use_spade = True

        self._sequence_group = request.POST.get("sequence_group", "None")
        if self._sequence_group == "None":
            self._sequence_group = request.POST.get("new_sequence_group", "")

            if self._sequence_group == "":
                template = loader.get_template(self.template_html)
                self.context.update({"error_found": True,
                                     "no_seq_group": "No sequence group specified"})

                self.response = HttpResponse(template.render(self._context, request))
                return not OK
            else:

                try:

                    group_tip = ViterbiSequenceGroupTip.objects.get(tip=self._sequence_group)
                except ObjectDoesNotExist as e:
                    model = ViterbiSequenceGroupTip()
                    model.tip = self._sequence_group
                    model.save()

        return OK

"""
class MultipleViterbiComputeForm(ComputeFormBase):

    def __init__(self, template_html, configuration, context):
        super(MultipleViterbiComputeForm, self).__init__(template_html=template_html,
                                                         context=context, configuration=configuration)

        self._path = INVALID_ITEM
        self._group_tip = INVALID_ITEM
        self._response = INVALID_ITEM
        self._chromosome = INVALID_ITEM
        self._ref_sequence_file = INVALID_ITEM
        self._wga_seq_filename = INVALID_ITEM
        self._no_wga_seq_filename = INVALID_ITEM
        self._hmm_name = INVALID_ITEM
        self._remove_dirs = INVALID_ITEM
        self._use_spade = INVALID_ITEM

    def as_map(self):
        return {"chromosome": self._chromosome,
                "hmm_name": self._hmm_name,
                "ref_seq_filename": self._ref_sequence_file,
                "wga_seq_filename": self._wga_seq_filename,
                "no_wga_seq_filename": self._no_wga_seq_filename,
                "path": self._path,
                "group_tip": self._group_tip,
                "remove_dirs": self._remove_dirs,
                "use_spade": self._use_spade}

    def check(self, request):

        self._hmm_name = request.POST.get("hmm", "")
        if self._hmm_name == "":
            return not OK

        self._chromosome = request.POST.get("chromosome", "")
        if self._chromosome == "":
            template = loader.get_template(self._template_html)
            self.context.update({"error_found": "No  chromosome specified"})
            self.response = HttpResponse(template.render(self._context, request))
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
            self.context.update({"error_found": True,
                                  "no_seq_chromosome": "No regions for chromosome {0}\
             and group {1}".format(self._chromosome, self._group_tip)})

            self.response = HttpResponse(template.render(self._context, request))
            return not OK

        region = objects[0]
        self._wga_seq_filename = region.wga_seq_file
        self._no_wga_seq_filename = region.no_wga_seq_file
        self._ref_sequence_file = region.ref_seq_file

        self._remove_dirs = request.POST.get('remove_dirs', False)
        if self._remove_dirs == 'True':
            self._remove_dirs = True

        self._use_spade = request.POST.get('use_spade', False)
        if self._use_spade == 'True':
            self._use_spade = True

        return OK
"""

class ViterbiComputeForm(ComputeFormBase):

    def __init__(self, template_html, configuration, context):

        super(ViterbiComputeForm, self).__init__(template_html=template_html,
                                                 context=context,
                                                 configuration=configuration)

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
                        "use_spade": INVALID_ITEM,
                        "sequence_group": INVALID_ITEM,
                        "scheduler_id": INVALID_ITEM}

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

        sequence_group = request.POST.get('sequence_group', "None")

        if sequence_group == "None":
            sequence_group = request.POST.get('new_sequence_group', "")

            if sequence_group == "":
                template = loader.get_template(self.template_html)
                self.context.update({"error_found": True,
                                     "no_seq_group": "No sequence group specified"})

                self.response = HttpResponse(template.render(self._context, request))
                return not OK
            else:

                try:

                    group_tip = ViterbiSequenceGroupTip.objects.get(tip=sequence_group)
                except ObjectDoesNotExist as e:
                    model = ViterbiSequenceGroupTip()
                    model.tip = sequence_group
                    model.save()

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
                        "use_spade": use_spade,
                        "sequence_group": sequence_group,
                        "scheduler_id": INVALID_ITEM}

        return OK


class SequenceComparisonComputeForm(ComputeFormBase):

    # name sof the distance metrics
    NAMES = TextDistanceCalculator.NAMES

    def __init__(self, template_html, configuration, context):
        super(SequenceComparisonComputeForm, self).__init__(template_html=template_html,
                                                            context=context,
                                                            configuration=configuration)

        self._kwargs = {'distance_metric': INVALID_ITEM,
                        'max_num_seqs': INVALID_ITEM,
                        'group_tip': INVALID_ITEM,
                        "scheduler_id": INVALID_ITEM}

    def as_map(self):
            return self._kwargs

    def check(self, request):

        group_tip = request.POST.get("group_tip", '')

        if group_tip == '':
            template = loader.get_template(self._template_html)
            self.context.update({"error_found": True,
                                  "error_msg": "No sequence group specified"})

            self.response = HttpResponse(template.render(self._context, request))
            return not OK

        self._kwargs['group_tip'] = group_tip
        max_num_seqs = request.POST.get("max_num_seqs", '')

        try:
            max_num_seqs = int(max_num_seqs)
            self._kwargs["max_num_seqs"] = max_num_seqs
        except ValueError as e:
            template = loader.get_template(self._template_html)
            self.context.update({"error_found": True,
                                 "error_msg": str(e)})

            self.response = HttpResponse(template.render(self._context, request))
            return not OK

        distance_metric = request.POST.get("distance_metric", '')

        if distance_metric == '':
            template = loader.get_template(self._template_html)
            self.context.update({"error_found": True,
                                 "error_msg": "No distance metric specified"})

            self.response = HttpResponse(template.render(self._context, request))
            return not OK

        self._kwargs['distance_metric'] = distance_metric
        return OK

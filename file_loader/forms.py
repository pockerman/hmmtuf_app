
from django.http import HttpResponse
from django.template import loader

from compute_engine import OK


class ErrorHandler(object):
    def __init__(self, filename, item_name, error_sponse_msg, template_html):
        self._filename = filename
        self._item_name = item_name
        self._template_html = template_html
        self._error_sponse_msg = error_sponse_msg
        self._response = None
        self._file = None
        self._name = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    @property
    def file_loaded(self):
        return self._file

    @property
    def name(self):
        return self._name

    def check(self, request):

        file_loaded = request.FILES.get(self._filename, None)

        if file_loaded is None:
            template = loader.get_template(self._template_html)
            self._response = HttpResponse(template.render({"error_missing_file":
                                                            self._error_sponse_msg["error_missing_file"]}, request))

        if self._response is not None:
            return not OK

        name = request.POST.get(self._item_name, '')
        if name == '':
            template = loader.get_template(self._template_html)
            self._response = HttpResponse(template.render({"error_missing_name":
                                                            self._error_sponse_msg["error_missing_name"]}, request))

        if self._response is not None:
            return not OK

        self._file = file_loaded
        self._name = name
        return OK


class RegionLoadForm(ErrorHandler):

    def __init__(self, filename, item_name, error_sponse_msg, template_html):
        super(RegionLoadForm, self).__init__(filename=filename, item_name=item_name,
                                             error_sponse_msg=error_sponse_msg, template_html=template_html)
        self._chromosome = None
        self._ref_seq_region = None
        self._wga_seq_region = None
        self._no_wga_seq_region = None

    @property
    def chromosome(self):
        return self._chromosome

    @property
    def ref_seq_region(self):
        return self._ref_seq_region

    @property
    def wga_seq_region(self):
        return self._wga_seq_region

    @property
    def no_wga_seq_region(self):
        return self._no_wga_seq_region

    def check(self, request):

        result = super(RegionLoadForm, self).check(request=request)

        if result is not OK:
            return not OK

        # did we also get the chromosome
        chromosome = request.POST.get('chr_name', '')

        if chromosome == '':
            template = loader.get_template(self._template_html)
            self._response = HttpResponse(template.render({"error_missing_chromosome_name": "Missing chromosome name"}, request))
            return not OK

        self._chromosome = chromosome
        self._ref_seq_region = request.POST.get('ref_seq_region', '')
        self._wga_seq_region = request.POST.get('wga_seq_region', '')
        self._no_wga_seq_region = request.POST.get('no_wga_seq_region', '')

        return OK







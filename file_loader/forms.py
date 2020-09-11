
from django.http import HttpResponse
from django.template import loader

from compute_engine import OK


class ErrorHandler(object):

    def __init__(self, filename, item_name, template_html):
        self._filename = filename
        self._item_name = item_name
        self._template_html = template_html
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
            self._response = HttpResponse(template.render({"error_found": "File not specified"}, request))

        if self._response is not None:
            return not OK

        name = request.POST.get(self._item_name, '')
        if name == '':
            template = loader.get_template(self._template_html)
            self._response = HttpResponse(template.render({"error_found": "Name not specified"}, request))

        if self._response is not None:
            return not OK

        self._file = file_loaded
        self._name = name
        return OK


class RegionLoadForm(ErrorHandler):

    def __init__(self, filename, item_name, context, template_html, path):
        super(RegionLoadForm, self).__init__(filename=filename, item_name=item_name,
                                             template_html=template_html)

        self._path = path
        self._context = context
        self._chromosome = None
        self._ref_seq_region = None
        self._wga_seq_region = None
        self._no_wga_seq_region = None
        self._start_idx = None
        self._end_idx = None

    @property
    def chromosome(self):
        return self._chromosome

    @property
    def ref_seq_filename(self):
        return self._path + self._ref_seq_region

    @property
    def wga_seq_filename(self):
        return self._path + self._wga_seq_region

    @property
    def no_wga_seq_filename(self):
        return self._path + self._no_wga_seq_region

    @property
    def start_idx(self):
        return self._start_idx

    @property
    def end_idx(self):
        return self._end_idx

    def check(self, request):

        file_loaded = request.FILES.get(self._filename, None)

        if file_loaded is None:
            template = loader.get_template(self._template_html)
            context = {"error_found": "File not specified"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._file = file_loaded

        name = request.POST.get(self._item_name, '')
        if name == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Name not specified"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._name = name

        # did we also get the chromosome
        chromosome = request.POST.get('chr_name', '')

        if chromosome == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Missing chromosome name"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        self._chromosome = chromosome
        self._ref_seq_region = request.POST.get('ref_seq_region', '')
        self._wga_seq_region = request.POST.get('wga_seq_region', '')
        self._no_wga_seq_region = request.POST.get('no_wga_seq_region', '')

        start_idx = request.POST.get('region_start_idx', '')

        if start_idx == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Missing start index"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        end_idx = request.POST.get('region_end_idx', '')

        if end_idx == '':
            template = loader.get_template(self._template_html)
            context = {"error_found": "Missing end index"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        try:
            self._start_idx = int(start_idx)
        except ValueError as e:
            template = loader.get_template(self._template_html)
            context = {"error_found": "Start index not an integer"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        try:

            self._end_idx = int(end_idx)
        except ValueError as e:
            template = loader.get_template(self._template_html)
            context = {"error_found": "End index not an integer"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        if self._start_idx >= self._end_idx:
            template = loader.get_template(self._template_html)
            context = {"error_found": "End index not strictly greater than start index"}
            context.update(self._context)
            self._response = HttpResponse(template.render(context, request))
            return not OK

        return OK







from django.http import HttpResponse
from django.template import loader
from file_loader.forms import BasicFileLoadErrorHandler

from compute_engine import OK


class LoadBedFile(object):

    def __init__(self, template_html):
        self._bed_checker = BasicFileLoadErrorHandler(filename="bed_filename")
        self._viterbi_checker = BasicFileLoadErrorHandler(filename="viterbi_filename")
        self._template_html = template_html

    def get_bed_file(self):
        return self._bed_checker.file_loaded

    def get_viterbi_file(self):
        return self._viterbi_checker.file_loaded

    def check(self, request):

        # check
        response = self._bed_checker.check(request=request)

        # if fail return an error message
        if response is not OK:
            template = loader.get_template(self._template_html)
            self.response = HttpResponse(template.render({"error_found": "Bed file not specified"}, request))
            return not OK

        response = self._viterbi_checker.check(request=request)

        if response is not OK:
            template = loader.get_template(self._template_html)
            self.response = HttpResponse(template.render({"error_found": "Viterbi file not specified"}, request))
            return not OK

        return  OK
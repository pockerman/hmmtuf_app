
from django.http import HttpResponse
from django.template import loader

OK = True


class ErrorHandler(object):
    def __init__(self, filename, item_name, error_sponse_msg, template_html):
        self._filename = filename
        self._item_name = item_name
        self._template_html = template_html
        self._error_sponse_msg = error_sponse_msg
        self._response = None
        self._file = None
        self._name = None

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

    def response(self):
        return self._response

    def get_file_loaded(self):
        return self._file

    def get_name(self):
        return self._name


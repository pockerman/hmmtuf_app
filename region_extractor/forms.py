

class ExtractRegionForm(object):

    @staticmethod
    def extract(form):

        request = form.request

        form.region_name = request.POST.get("region_name", "")
        if form.region_name == "":
            return "Region name is not specified"

        form.ref_file = request.POST.get("ref_file", "")
        if form.ref_file == "":
            return "Reference filename is not specified"

        form.wga_ref_seq_file = request.POST.get("wga_ref_seq_file", "")
        if form.wga_ref_seq_file == "":
            return "WGA filename is not specified"

        form.nwga_ref_seq_file = request.POST.get("nwga_ref_seq_file", "")
        if form.nwga_ref_seq_file == "":
            return "No-WGA filename is not specified"

        form.region_start = request.POST.get("region_start", "")
        if form.region_start == "":
            return "Region start is not specified"

        form.region_start = int(form.region_start)

        form.region_end = request.POST.get("region_end", "")
        if form.region_end == "":
            return "Region end is not specified"

        form.region_end = int(form.region_end)

        if form.region_end <= form.region_start:
            return "Region end cannot be less than or equal to region start"

        form.window_size = request.POST.get("window_size", "")
        if form.window_size == "":
            form.window_size = 100
        else:
            form.window_size = int(form.window_size)

        form.chromosome = request.POST.get("chromosome", "")
        if form.chromosome == "":
            return "Chromosome is not specified"

        form.outlier_remove = request.POST.get("outlier_remove", "")
        if form.outlier_remove == "":
            return "Chromosome is not specified"

        form.max_depth = request.POST.get("max_depth", "")
        if form.max_depth == "":
            form.max_depth = 1000
        else:
            form.max_depth = int(form.max_depth)

        form.ignore_orphans = request.POST.get("ignore_orphans", False)
        form.truncate = request.POST.get("truncate", False)
        form.add_indels = request.POST.get("add_indels", True)

        form.quality_threshold = request.POST.get("quality_threshold", "")

        if form.quality_threshold == "":
            form.quality_threshold = 20
        else:
            form.quality_threshold = int(form.quality_threshold)

        return True

    def __init__(self, request):
        self.request = request
        self.quality_threshold = ""
        self.add_indels = ""
        self.truncate = ""
        self.ignore_orphans = ""
        self.max_depth = ""
        self.outlier_remove = ""
        self.chromosome = ""
        self.window_size = ""
        self.region_end = ""
        self.region_start = ""
        self.nwga_ref_seq_file = ""
        self.wga_ref_seq_file = ""
        self.ref_file = ""
        self.region_name = ""
        self.processing = "serial"
        self.check_windowing_sanity = True

    def as_dict(self):
        return {"quality_threshold": self.quality_threshold,
                "add_indels": self.add_indels,
                "truncate": self.truncate,
                "ignore_orphans": self.ignore_orphans,
                "max_depth": self.max_depth,
                "outlier_remove": self.outlier_remove,
                "chromosome": self.chromosome,
                "window_size": self.window_size,
                "region_end": self.region_end,
                "region_start": self.region_start,
                "nwga_ref_seq_file": self.nwga_ref_seq_file,
                "wga_ref_seq_file": self.wga_ref_seq_file,
                "ref_file": self.ref_file,
                "region_name": self.region_name,
                "processing": self.processing,
                "check_windowing_sanity": self.check_windowing_sanity}





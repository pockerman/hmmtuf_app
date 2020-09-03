

class ExtractRegionForm(object):

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

    @staticmethod
    def extract(form):

        request = form.request

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

        if form.region_end<=form.region_start:
            return "Region end cannot be less than or equal to region start"

        form.window_size = request.POST.get("window_size", 100)
        #if form.window_size == "":
        #    return "Window size is not specified"
        form.window_size = int(form.window_size)

        form.chromosome = request.POST.get("chromosome", "")
        if form.chromosome == "":
            return "Chromosome is not specified"

        form.outlier_remove = request.POST.get("outlier_remove", "")
        if form.outlier_remove == "":
            return "Chromosome is not specified"

        form.max_depth = request.POST.get("max_depth", 1000)
        if form.max_depth == "":
            return "Maximum depth is not specified"

        form.max_depth = int(form.max_depth)

        form.ignore_orphans = request.POST.get("ignore_orphans", False)
        form.truncate = request.POST.get("truncate", False)
        form.add_indels = request.POST.get("add_indels", True)

        form.quality_threshold = request.POST.get("quality_threshold", "")
        if form.quality_threshold == "":
            return "Quality threshold is not specified"

        form.quality_threshold = int(form.quality_threshold)






        return True



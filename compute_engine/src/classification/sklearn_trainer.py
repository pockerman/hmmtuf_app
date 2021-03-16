
class SKLearnTrainer(object):
    """
    Class for training sklearn models
    """
    def __init__(self, **options):
        self._options = options

    def train(self):

        data_loader = self._options["data_loader"]
        self._options["model"].fit(X=data_loader.get_data_set(),
                                   y=data_loader.get_labels())
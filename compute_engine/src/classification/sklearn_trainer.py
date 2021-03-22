from compute_engine.src.classification.logistic_regressor import SKLearnLogisticRegressor

class SKLearnTrainer(object):
    """
    Class for training sklearn models
    """
    def __init__(self, options) -> None:
        self._options = options
        self._model = SKLearnLogisticRegressor(options=options)

    @property
    def model(self) -> SKLearnLogisticRegressor:
        return self._model

    def train(self) -> None:
        """
        Train the underlying model
        """

        data_loader = self._options["data_loader"]
        self._model.fit(X=data_loader.get_data_set,
                        y=data_loader.get_labels)


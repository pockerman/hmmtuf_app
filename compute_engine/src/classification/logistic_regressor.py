from compute_engine.src.enumeration_types import ClassifierType
from compute_engine.src.cengine_configuration import HAS_SKLEARN, HAS_PYTORCH
from compute_engine.src.classification.classifier_base import ClassifierBase

if HAS_SKLEARN:
    from sklearn.linear_model import LogisticRegression



class LogisticRegressor(ClassifierBase):

    def __init__(self, regressor_type, **options):

        if regressor_type == ClassifierType.SKLEARN_LOGISTIC_REGRESSOR:
            self._regressor_impl = SKLearnLogisticRegressor(**options)
        elif regressor_type == ClassifierType.PYTORCH_LOGISTIC_REGRESSOR:
            self._regressor_impl = PyTorchLogisticRegressor(**options)
        else:
            raise ValueError("Invalid regressor type")

    @abstractmethod
    def predict(self, x):
        """
        Predict based on the input data
        """
        return self._regressor_impl.predict(x=x)

    @abstractmethod
    def __call__(self, x):
        pass

class SKLearnLogisticRegressor(LogisticRegressor):
    """
    Wrapper to SKLearn Logistic Regression model
    """

    REGRESSOR_TYPE = ClassifierType.SKLEARN_LOGISTIC_REGRESSOR

    def __init__(self, **options):
        self._options = options
        self._model = LogisticRegression()

    @abstractmethod
    def predict(self, x):
        """
        Predict based on the input data
        """
        return self._model.predict(X=x)

    @abstractmethod
    def __call__(self, x):
        return self.predict(x=x)

class PyTorchLogisticRegressor(LogisticRegressor):

    REGRESSOR_TYPE = ClassifierType.PYTORCH_LOGISTIC_REGRESSOR

    def __init__(self, **options):
        self._options = options

    @abstractmethod
    def predict(self, x):
        """
        Predict based on the input data
        """
        pass

    @abstractmethod
    def __call__(self, x):
        pass


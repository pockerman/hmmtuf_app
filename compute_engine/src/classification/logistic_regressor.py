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

    def get_parameters(self):
        """
        Return the parameters of the model
        """
        return self._regressor_impl.get_parameters()

    def predict(self, x):
        """
        Predict based on the input data
        """
        return self._regressor_impl.predict(x=x)

    def __call__(self, x):
        return self.predict(x=x)

class SKLearnLogisticRegressor():
    """
    Wrapper to SKLearn Logistic Regression model
    """

    # the type of the regressor
    REGRESSOR_TYPE = ClassifierType.SKLEARN_LOGISTIC_REGRESSOR

    def __init__(self, options):
        # the options passed to the model
        self._options = options

        # the model
        self._model = self._initialize()

    def get_parameters(self):
        """
        Return the parameters of the model
        """
        return self._model.get_params()

    def predict(self, x):
        """
        Predict based on the input data
        """
        return self._model.predict(X=x)

    def __call__(self, x):
        return self.predict(x=x)

    def fit(self, X, y):
        """
        Fit the model
        """
        self._model.fit(X=X, y=y)

    def _initialize(self):
        """
        Create the model based on the assigned
        """

        max_itrs = self._options["max_iter"] if "max_iter" in self._options else 100
        fit_intercept = self._options["fit_intercept"] if "fit_intercept" in self._options else True
        verbose = self._options["verbose"] if "verbose" in self._options else True
        tol = self._options["tol"] if "tol" in self._options else 1.0e-4
        solver = self._options["solver"] if "solver" in self._options else 'lbfgs'
        n_jobs = self._options["n_jobs"] if "n_jobs" in self._options else 1
        return LogisticRegression(max_iter=max_itrs, verbose=verbose, fit_intercept=fit_intercept,
                                  tol=tol, solver=solver, n_jobs=n_jobs)

class PyTorchLogisticRegressor(LogisticRegressor):

    REGRESSOR_TYPE = ClassifierType.PYTORCH_LOGISTIC_REGRESSOR

    def __init__(self, **options):
        self._options = options

    def predict(self, x):
        """
        Predict based on the input data
        """
        pass

    def __call__(self, x):
        pass


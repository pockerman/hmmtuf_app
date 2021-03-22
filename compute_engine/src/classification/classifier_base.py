from abc import abstractmethod

class ClassifierBase(object):
    def __init__(self):
        pass

    @abstractmethod
    def predict(self, x):
        """
        Predict based on the input data
        """
        pass

    @abstractmethod
    def __call__(self, x):
        pass
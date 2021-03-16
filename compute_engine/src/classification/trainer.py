
from compute_engine.src.enumeration_types import BackendType
from compute_engine.src.cengine_configuration import HAS_SKLEARN, HAS_PYTORCH

if HAS_SKLEARN:
    from compute_engine.src.classification.sklearn_trainer import SKLearnTrainer

if HAS_PYTORCH:
    from compute_engine.src.classification.pytorch_trainer import PyTorchTrainer

class Trainer(object):
    """
    Wrapper class for training supervised models
    """

    def __init__(self, options):
        self._options = options

    def train(self):
        """
        Train the model
        """

        print(self._options)
        if self._options["backend_type"] == BackendType.SKLEARN:
            trainer = SKLearnTrainer(**self._options)
            trainer.train()
        elif self._options["backend_type"] == BackendType.PYTORCH:
            trainer = PyTorchTrainer(**self._options)
            trainer.train()
        else:
            raise ValueError("Invalid backend type")




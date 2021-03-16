import numpy as np
from pathlib import Path
import csv
import pandas as pd

class SimpleDataLoader(object):
    """
    Simple data loader. Stores in RAM
    the entire dataset and provides access to it on demand
    """
    def __init__(self):
        self._X = None
        self._labels = None

    @property
    def get_data_set(self) -> np.array:
        return self._X

    @get_data_set.setter
    def get_data_set(self, X: np.array) -> None:
        self._X = X

    @property
    def get_labels(self) -> np.array:
        return self._labels

    @get_labels.setter
    def get_labels(self, labels: np.array) -> None:
        self._labels = labels

    def read_from_csv(self, filename: Path, label_idx: int=-1,
                      delimiter: str=",", comment_mark: str='#') -> None:

        data_frame = pd.read_csv(filepath_or_buffer=filename, delimiter=delimiter)
        columns = data_frame.columns
        self._labels = data_frame[columns[label_idx]].to_numpy()
        columns.


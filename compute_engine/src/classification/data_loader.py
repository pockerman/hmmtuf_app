import numpy as np
from pathlib import Path
import csv
import pandas as pd

class SimpleDataLoader(object):
    """
    Simple data loader. Stores in RAM
    the entire dataset and provides access to it on demand
    """

    def __init__(self, X: np.array=None, labels: np.array=None) -> None:
        self._X = X
        self._labels = labels

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

    def get_n_class_labels(self, class_idx: int) -> int:
        """
        Returns the number of occurences of the
        given class index
        """
        return np.count_nonzero(self._labels ==  class_idx)

    def read_from_csv(self, filename: Path, label_idx: int=-1,
                      delimiter: str=",") -> None:
        """
        Read the data from the given filename
        :param filename:
        :param label_idx: The index in the columns that denotes the labels
        :param delimiter: The delimiter to usde
        :return: None
        """

        data_frame = pd.read_csv(filepath_or_buffer=filename, delimiter=delimiter)
        columns = data_frame.columns
        self._labels = data_frame[columns[label_idx]].to_numpy()
        columns = columns.delete(label_idx)
        self._X = data_frame[columns].to_numpy()

    def __len__(self):
        return self._X.shape[0]


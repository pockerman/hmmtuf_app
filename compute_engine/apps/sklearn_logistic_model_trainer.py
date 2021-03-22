import sys
import numpy as np
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
#if "/home/alex/qi3/hmmtuf" not in sys.path:
#    sys.path.append("/home/alex/qi3/hmmtuf")

from db.sqlite3_db_connector import SQLiteDBConnector
from compute_engine.src.classification.trainer import Trainer
from compute_engine.src.classification.logistic_regressor import LogisticRegressor
from compute_engine.src.enumeration_types import ClassifierType
from compute_engine.src.enumeration_types import BackendType
from compute_engine.src.classification.data_loader import SimpleDataLoader
from compute_engine.src.utils import INFO


def create_data_loader():

    name_to_index = {"TUF": 0, "TUFDUP": 0,
                     "Normal-I": 1, "Normal-II": 1,
                     "Duplication": 1, "Deletion": 1, "GAP_STATE": 5}

    filename = Path("/home/alex/qi3/hmmtuf/data/chr1_repeats/region_1/viterbi_path.csv")
    
    with open(filename, 'r', newline="\n") as fh:
        reader = csv.reader(fh, delimiter=":")
        
        X_tuf = []
        X_non_tuf = []
        y = []
        for row in reader:
            
            if len(row) != 5:
                continue

            if row[4] == 'GAP_STATE':
                continue
                
            means_str = row[3].split(",")
            means_str[0] = means_str[0].strip('(,)')
            means_str[1] = means_str[1].strip('(,)')
            label = row[4]

            X_tuf.append
            X.append(float(means_str[1]))
            y.append(name_to_index[label])
            
        X = np.array(X)
        X = X.reshape(-1, 1)
        y = np.array(y)

        X_train, y_train, _ =  train_test_split(X, y, test_size=0.33, random_state=42)
        data_frame = SimpleDataLoader(X=X_train, labels=y_train)
        return data_frame


def main():
    data_loader = create_data_loader()
    print("{0} number of points {1}".format(INFO, len(data_loader)))
    print("{0} number of points for class 0 {1}".format(INFO, data_loader.get_n_class_labels(class_idx=0)))
    print("{0} number of points for class 1 {1}".format(INFO, data_loader.get_n_class_labels(class_idx=1)))
    trainer_options = {"model": ClassifierType.SKLEARN_LOGISTIC_REGRESSOR,
                       "backend_type": BackendType.SKLEARN,
                       "data_loader": data_loader,
                       "max_iter": 1000,
                       "verbose": True, "fit_intercept": True,
                       "tol": 1.0e-8, "random_state": 0,
                       "solver":'newton-cg',
                       "n_jobs": 3}

    # the trainer class
    trainer = Trainer(options=trainer_options)

    # train
    trainer.train()


if __name__ == '__main__':
    main()





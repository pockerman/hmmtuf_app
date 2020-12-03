import numpy as np
from compute_engine.src.constants import INFO

from compute_engine.src.utils import to_csv_line
from spark_integration.spark_manager import SparkManager


if __name__ == '__main__':

    APP_NAME = "ComputeSequencesLengthApp"
    print("{0} Running {1} application".format(INFO, APP_NAME))

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "lengths.txt"

    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    INPUT_FILE = "full_sequences.csv"

    manager = SparkManager(master_url="local",
                           app_name=APP_NAME)

    print("{0} Loading sequences from {1}".format(INFO, INPUT_DIR + INPUT_FILE))

    # load the sequences
    sequences = manager.load_rdd_from_text_file(filename=INPUT_DIR + INPUT_FILE)

    print("{0} Creating sequences length...".format(INFO))

    # compute feature vectors
    sequences_length = sequences.map(lambda seq: len(seq)).cache()

    print("{0} Computing statistics...".format(INFO))

    # compute the distances
    mean = sequences_length.mean()
    var = sequences_length.variance()

    print("{0} Mean={1} , Variance={2}".format(INFO, mean, var))

    # save the distances
    manager.save_rdd_to_text_file(filename=OUTPUT_DIR + OUTPUT_FILE,
                                  rdd=sequences_length, mapper=to_csv_line)

    print("{0} Finished...".format(INFO))
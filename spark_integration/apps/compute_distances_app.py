import numpy as np
from compute_engine.src.constants import INFO

from compute_engine.src.utils import to_csv_line
from compute_engine.src.cpf import sequence_feature_vector
from spark_integration.spark_manager import SparkManager


if __name__ == '__main__':

    APP_NAME = "ComputeDistancesApp"
    print("{0} Running {1} application".format(INFO, APP_NAME))

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "full_sequences_distances"

    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/input/"
    INPUT_FILE = "full_sequences.csv"

    manager = SparkManager(master_url="local",
                           app_name=APP_NAME)

    print("{0} Loading sequences from {1}".format(INFO, INPUT_DIR + INPUT_FILE))

    # load the sequences
    sequences = manager.load_rdd_from_text_file(filename=INPUT_DIR + INPUT_FILE)

    print("{0} Creating feature vectors...".format(INFO))

    # compute feature vectors
    feature_vectors = sequences.map(lambda seq: sequence_feature_vector(seq))

    print("{0} Building cartesian product...".format(INFO))

    # form pairs of the sequences
    cartesian_product = feature_vectors.cartesian(feature_vectors)

    print("{0} Computing distances...".format(INFO))

    # compute the distances
    distances = cartesian_product.map(lambda pair: np.linalg.norm(np.array(pair[0]) - np.array(pair[1])))

    print("{0} Writing output to {1} ".format(INFO, OUTPUT_DIR + OUTPUT_FILE))

    # save the distances
    manager.save_rdd_to_text_file(filename=OUTPUT_DIR + OUTPUT_FILE,
                                  rdd=distances, mapper=to_csv_line)

    print("{0} Finished...".format(INFO))

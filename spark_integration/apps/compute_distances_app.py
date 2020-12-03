from compute_engine.src.constants import INFO
from compute_engine.src.utils import to_csv_line
from compute_engine.src.string_sequence_calculator import TextDistanceCalculator
from spark_integration.spark_manager import SparkManager


if __name__ == '__main__':

    APP_NAME = "ComputeDistancesApp"
    print("{0} Running {1} application".format(INFO, APP_NAME))

    DISTANCE_TYPE = "Longest common substring similarity"

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    #OUTPUT_FILE = "random_sequences_distances" + "_longest_common_substring_similarity"
    OUTPUT_FILE = "full_sequences_distances" + "_longest_common_substring_similarity"

    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/input/"
    INPUT_FILE = "full_sequences.csv"
    #INPUT_FILE = "random_sequences.csv"

    manager = SparkManager(master_url="local",
                           app_name=APP_NAME)

    print("{0} Loading sequences from {1}".format(INFO, INPUT_DIR + INPUT_FILE))

    # load the sequences
    sequences = manager.load_rdd_from_text_file(filename=INPUT_DIR + INPUT_FILE)

    print("{0} Building cartesian product...".format(INFO))

    # form pairs of the sequences
    sequences_cartesian_product = sequences.cartesian(sequences)

    print("{0} Calculating distances".format(INFO))
    print("{0} Using distance metric {1}".format(INFO, DISTANCE_TYPE))
    distances = sequences_cartesian_product.map(lambda pair: TextDistanceCalculator.build_calculator(name=DISTANCE_TYPE).similarity(pair[0], pair[1]))

    print("{0} Writing output to {1} ".format(INFO, OUTPUT_DIR + OUTPUT_FILE))

    # save the distances
    manager.save_rdd_to_text_file(filename=OUTPUT_DIR + OUTPUT_FILE,
                                  rdd=distances, mapper=to_csv_line)

    print("{0} Finished...".format(INFO))

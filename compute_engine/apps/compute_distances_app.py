import csv
import numpy as np
from compute_engine.src.constants import INFO
from compute_engine.src.utils import to_csv_line
from compute_engine.src.string_sequence_calculator import TextDistanceCalculator


def load_sequences_files(filename):

    with open(filename, 'r', newline="\n") as fh:
        file_reader = csv.reader(fh, delimiter=",")

        sequences = []
        for line in file_reader:
            sequences.append(line[0])

        return sequences


def compute_sequences_cartesian_product(sequences):

    cartesian_product = []

    for i in range(len(sequences)):
        for j in range(len(sequences)):
            if i != j:
                cartesian_product.append((sequences[i], sequences[j]))
    return cartesian_product


def compute_distances(distance_type, sequences, use_partial_sums=True,
                      store_average_length=False, store_total_length=False):

    if store_average_length and store_total_length:
        raise ValueError("Cannot save both average length and total length")

    calculator = TextDistanceCalculator.build_calculator(name=distance_type)

    if distance_type == 'CPF':
        calculator._use_partial_sums = use_partial_sums

    distances = []
    if store_average_length:

        for item in sequences:
            distances.append((np.mean([len(item[0]), len(item[1])]),
                              calculator.similarity(item[0], item[1])))

    else:

        for item in sequences:
            distances.append(calculator.similarity(item[0], item[1]))
    return distances


def save_distances(filename, distances):

    with open(filename, 'w', newline="\n") as fh:
        writer = csv.writer(fh, delimiter=",")
        dim = len(distances[0])
        for item in distances:

            if dim == 1:
                writer.writerow([item])
            else:
                writer.writerow(item)


if __name__ == '__main__':

    APP_NAME = "ComputeDistancesApp"
    print("{0} Running {1} application".format(INFO, APP_NAME))

    DISTANCE_TYPE = "CPF"
    STORE_AVERAGE_LENGTH = True
    STORE_TOTAL_LENGTH = False


    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "random_sequences_distances_with_average_length" + "_CPF.csv"
    #OUTPUT_FILE = "full_sequences_distances_with_average_length" + "_CPF.csv"

    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/input/"
    #INPUT_FILE = "full_sequences.csv"
    INPUT_FILE = "random_sequences_II.csv"

    print("{0} Loading sequences from {1}".format(INFO, INPUT_DIR + INPUT_FILE))

    # load the sequences
    sequences = load_sequences_files(filename=INPUT_DIR + INPUT_FILE)

    print("{0} Building cartesian product...".format(INFO))

    # form pairs of the sequences
    sequences_cartesian_product = compute_sequences_cartesian_product(sequences)

    print("{0} Calculating distances".format(INFO))
    print("{0} Using distance metric {1}".format(INFO, DISTANCE_TYPE))
    distances = compute_distances(distance_type=DISTANCE_TYPE,
                                  sequences=sequences_cartesian_product,
                                  use_partial_sums=True,
                                  store_average_length=STORE_AVERAGE_LENGTH,
                                  store_total_length=STORE_TOTAL_LENGTH)

    print("{0} Writing output to {1} ".format(INFO, OUTPUT_DIR + OUTPUT_FILE))

    # save the distances
    save_distances(filename=OUTPUT_DIR + OUTPUT_FILE, distances=distances)

    print("{0} Finished...".format(INFO))

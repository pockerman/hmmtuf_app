import csv
from compute_engine.src.string_sequence_calculator import TextDistanceCalculator


def save_feature_vectors(filename, vectors):

    with open(filename, 'w', newline="\n") as fh:
        writer = csv.writer(fh, delimiter=",")

        for item in vectors:
                writer.writerow(item)

def create_12_dim_vectors_app_main(input_dir, input_file, output_dir, output_filename):

    with open(input_dir + input_file, 'r', newline='\n') as rfh:

        calculator = TextDistanceCalculator.build_calculator(name='CPF')
        calculator._use_probability_counts = True
        file_reader = csv.reader(rfh, delimiter=',')

        sequences = []
        for line in file_reader:
            calculator.add_feature_vector(seq=line[0])
            sequences.append(line[0])

        feature_vectors = calculator.get_feature_vectors()

        data = []
        for seq, vec in zip(sequences, feature_vectors):
            row = [seq]
            for item in vec:
                row.append(item)
            data.append(row)

        save_feature_vectors(filename=output_dir + output_filename,
                             vectors=data)

if __name__ == '__main__':
    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    INPUT_FILE = "normal_sequences.csv"

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "normal_repeats_probability_counts_vectors.csv"

    create_12_dim_vectors_app_main(input_dir=INPUT_DIR, input_file=INPUT_FILE,
                                   output_dir=OUTPUT_DIR, output_filename=OUTPUT_FILE)
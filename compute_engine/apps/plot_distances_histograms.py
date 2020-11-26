import seaborn as sns
import csv
import numpy as np
import matplotlib.pyplot as plt


def plot_distances_hist_main(output_dir, output_file, line_index,
                             title, xlabel):

    with open(output_dir + output_file, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []

        for line in reader:
            x.append(float(line[line_index]))

        print("Number of items {0}".format(len(x)))

        #sns.histplot(data=x, bins=40)
        sns.kdeplot(data=x)
        plt.title(title)
        # plt.xlim(xmin=0, xmax=100)
        plt.xlabel(xlabel)
        plt.show()


if __name__ == '__main__':

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/test_random_distances/"
    OUTPUT_FILE = "part-00000"
    LINE_INDEX = -1

    plot_distances_hist_main(output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE,
                             line_index=LINE_INDEX, title="Random sequences",
                             xlabel="L2 Norm")

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/full_sequences_distances/"

    plot_distances_hist_main(output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE,
                             line_index=LINE_INDEX, title="Extracted sequences",
                             xlabel="L2 Norm")



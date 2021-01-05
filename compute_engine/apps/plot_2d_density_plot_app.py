import csv
import numpy as np
import matplotlib.pyplot as plt


def get_data(data_dir, data_file):

    with open(data_dir + data_file, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []
        y = []

        for line in reader:
            x.append(float(line[0]))
            y.append(float(line[1]))

        print("Number of items {0}".format(len(x)))
        return x, y


def main(data_dir, data_file, bins,
         plot_title, plot_xlabel, plot_ylabel,
         plot_xlim, plot_ylim):

    x, y = get_data(data_dir=data_dir, data_file=data_file)

    print("Max average length={0}".format(np.max(x)))
    print("Mean average length={0}".format(np.mean(x)))
    print("Max distance={0}".format(np.max(y)))
    print("Mean distance={0}".format(np.mean(y)))

    plt.title(plot_title)
    plt.xlabel(plot_xlabel)
    plt.ylabel(plot_ylabel)

    if plot_xlim is not True and plot_ylim is not True:
        plt.hist2d(x, y, bins=bins, cmap=plt.cm.jet, alpha=0.5, range=[plot_xlim, plot_ylim])
    else:
        plt.hist2d(x, y, bins=bins, cmap=plt.cm.jet, alpha=0.5)

    plt.show()


if __name__ == '__main__':

    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    #INPUT_FILE = "random_deletion_sequences_distances_with_average_length_CPF_PROBABILITY_COUNTS_REMOVE_ZEROS.csv"
    INPUT_FILE = "full_deletion_sequences_distances_with_average_length_CPF_PROBABILITY_COUNTS_REMOVE_ZEROS.csv"

    PLOT_TITLE = "Extracted Deletion Repeats CPF counts P Remove 0s"
    PLOT_X_LABEL = "Average Length"
    PLOT_Y_LABEL = "Distance"
    BINS = (100, 100)

    PLOT_X_LIM = (0, 100)
    PLOT_Y_LIM = (0, 3)

    main(data_dir=INPUT_DIR, data_file=INPUT_FILE, bins=BINS,
         plot_title=PLOT_TITLE, plot_xlabel=PLOT_X_LABEL, plot_ylabel=PLOT_Y_LABEL,
         plot_xlim=PLOT_X_LIM, plot_ylim=PLOT_Y_LIM)

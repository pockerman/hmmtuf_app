import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

from compute_engine.src.m_kmeans import MbKMeans
from compute_engine.src.cpf import CPF
from compute_engine.src.cpf import sequence_feature_vector
from compute_engine.src.utils import compute_textdistances
from compute_engine.src.utils import read_bed_files
from compute_engine.src.constants import INFO
from compute_engine.src.utils import min_size_partition_range


class L2Norm(object):

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return np.linalg.norm(args[0] - args[1])


def find_smallest_sequence(seqs):

    min_size = len(seqs[list(seqs.keys())[0]])
    sequence = seqs[list(seqs.keys())[0]]
    for seq in seqs:
        if len(seqs[seq]) < min_size:
            min_size = len(seqs[seq])
            sequence = seqs[seq]
    return min_size, sequence


def chunck_sequence(seq, size):

    chuncks = []
    chunck_items = min_size_partition_range(start=0, end=len(seq), minsize=size)

    for chunck_item in chunck_items:
        start = chunck_item[0]
        end = chunck_item[1]

        cseq = ""
        for i in range(start, end, 1):
            cseq += seq[i]
        chuncks.append(cseq)
    return chuncks


def bisect_seqs(seqs, size):

    sequences = []
    for s in seqs:
        seq = seqs[s]

        if len(seq) > size:
            # break up the sequence into size chuncks
            sequences.extend(chunck_sequence(seq=seq, size=size))
        else:
            sequences.append(seq)

    return sequences


def save_distances(output_dir, output_file, dist_map, remove_existing):

    dir_folder = Path(output_dir)
    files = os.listdir(dir_folder)

    if output_file not in files:
        mode = 'w'
    elif output_file in files and not remove_existing:
        mode = 'a'
    else:
        mode = 'w'

    print("{0} Write output distances in {1}".format(INFO, dir_folder / output_file))

    with open(dir_folder / output_file, mode) as f:
        for item in dist_map:
            f.write(item[0] + ',' + item[1] + ',' + str(dist_map[item]) + '\n')


if __name__ == '__main__':

    output_dir = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    output_file = "sequences_dist.csv"
    file_dir = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/data/chr1_repeats/"
    filenames = ["region_1/nucl_out.bed", "region_2/nucl_out.bed", "region_3/nucl_out.bed",
                 "region_4/nucl_out.bed", "region_5/nucl_out.bed", "region_6/nucl_out.bed",
                 "region_7/nucl_out.bed", "region_8/nucl_out.bed", "region_9/nucl_out.bed",
                 "region_10/nucl_out.bed", "region_11/nucl_out.bed", "region_12/nucl_out.bed",
                 "region_13/nucl_out.bed"]

    seqs = read_bed_files(file_dir=file_dir, filenames=filenames, concatenate=False)

    print("{0} Number of bed sequences extracted from bed files: {1}".format(INFO, len(seqs)))

    for s in seqs:
        #print("{0} seq={1}".format(INFO, seqs[s]))

        if seqs[s] == 'TCCC':
            print("{0} seq={1}".format(INFO, seqs[s]))
            v = sequence_feature_vector(seq=seqs[s], k=2)
            print("{0} v={1}".format(INFO, v))


    #min_size, sequence = find_smallest_sequence(seqs=seqs)
    #sequences = bisect_seqs(seqs=seqs, size=min_size)
    #print("{0} Number of sequences for analysis {1}".format(INFO, len(sequences)))
    #print(sequnces)

    """
    distances = compute_textdistances(sequences=seqs, distance_type=CPF(),
                                      build_from_factory=False, compute_self_distances=False)
    """

    """
    save_distances(output_dir=output_dir, output_file=output_file,
                   dist_map=distances, remove_existing=True)
    """

    """
    with open(output_dir + output_file, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []

        for line in reader:
            x.append(float(line[2]))

        print("Number of distances {0}".format(len(x)))
        axes = sns.histplot(data=x, bins=20)
        plt.title("Chr1 Regions sequences")
        plt.xlabel("L2-Norm")
        plt.show()
    """

    """
    distances = compute_textdistances(seq_dict=seqs, distance_type=CPF(), build_from_factory=False)
    save_distances(output_dir=output_dir, output_file=output_file,
                   dist_map=distances, remove_existing=True)

    # use CPF to convert in a 12-dim
    # shannon entropy vectors

    distance_metric = CPF()
    seq_to_idx = dict()

    counter = 0
    for item in seqs:
        distance_metric.add_feature_vector(seq=seqs[item])
        seq_to_idx[counter] = item
        counter += 1

    data = distance_metric.get_feature_vectors()

    kmeans = MbKMeans(distance_metric=L2Norm(), iterations=10, tolerance=1.0e-5,
                      n_clusters=5, initializer=None,
                      use_largest_cluster_to_bisect=False,
                      verbose=True, n_bisection_iterations=10, use_sklearn_kmeans=True)

    kmeans.cluster(dataset=data)

    clusters = kmeans.clusters

    colors = ['ro', 'bo', 'yo', 'go', 'mo', 'ko']
    """

    """
    for cluster in clusters:
        print("Cluster id {0}".format(cluster.idx))
        print("Number of instances {0}".format(len(cluster.indexes)))

        x = []
        y = []

        for idx in cluster.indexes:
            x.append(data[idx][0])
            y.append(data[idx][1])
        plt.plot(x, y, colors[cluster.idx])
    plt.show()
    """

    """
    with open(output_dir + output_file, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []

        for line in reader:
            x.append(float(line[2]))

        print("Number of distances {0}".format(len(x)))
        axes = sns.histplot(data=x, bins=20)
        plt.title("Chr1 Regions sequences")
        plt.xlabel("L2-Norm")
        plt.show()
    """







import csv
import pandas as pnd
import copy
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from compute_engine.src.utils import count_kmers

import seaborn as sns

sns.set_theme(style="whitegrid")

def get_data(data_dir, data_file):

    with open(data_dir + data_file, 'r') as fh:
        reader = csv.reader(fh, delimiter=",")

        x = []
        sequences = []
        for line in reader:
            sequences.append(line[0])
            row = [float(item) for item in line[1:]]
            x.append(row)
        return sequences, x


def apply_clustering_app_main(data, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(data)
    return kmeans.labels_


def save_clusters(output_dir, output_file, sequences, labels):

    with open(output_dir + output_file, 'w') as fh:
        writer = csv.writer(fh, delimiter=",")

        for seq, label in zip(sequences, labels):
            writer.writerow([seq, label])

def save_kmers(output_dir, output_file, seq_kmers_cluster_0, seq_kmers_cluster_1):

    with open(output_dir + output_file, 'w') as fh:
        writer = csv.writer(fh, delimiter=",")

        for item in seq_kmers_cluster_0:
            row = [0, item, seq_kmers_cluster_0[item]]
            writer.writerow(row)

        for item in seq_kmers_cluster_1:
            row = [1, item, seq_kmers_cluster_1[item]]
            writer.writerow(row)


def get_cluster_kmers(cluster, used_kmers, k):

    seq_kmers_cluster = {}
    total_counter = 0

    for seq in cluster:

        # get kmers for sequence
        kmers = count_kmers(sequence=seq, k=k)

        if len(kmers) != 0:

            # sort the kmers in ascending order
            sorted_counts = {k: v for k, v in sorted(kmers.items(), key=lambda item: item[1])}

            keys = list(sorted_counts.keys())
            total_counter += len(keys)

            top_scored = []

            # if we have not specified which kmers then
            # return all the kmers
            if len(used_kmers) == 0:
                for name in keys:
                    top_scored.append((name, sorted_counts[name]))
            else:
                # otherwise from the sorted
                # kmers only pick what is asked
                for item in used_kmers:
                    top_scored.append((keys[item], sorted_counts[keys[item]]))

            seq_kmers_cluster[seq] = top_scored

    return seq_kmers_cluster, total_counter


def get_kmers_frequency(seq_kmers_cluster):

    totals_kmers_cluster = {}

    for item in seq_kmers_cluster:

        vals = seq_kmers_cluster[item]

        for val in vals:

            kmer = val[0]

            if kmer in totals_kmers_cluster:
                totals_kmers_cluster[kmer] += 1
            else:
                totals_kmers_cluster[kmer] = 1

    return totals_kmers_cluster

def get_sorted_totals(total_kmers, used_entries=[-1, -2, -3, -4, -5]):
    sorted_totals = {k: v for k, v in sorted(total_kmers.items(), key=lambda item: item[1])}
    keys = list(sorted_totals.keys())

    top_5_result = {}

    if len(used_entries) == 0 or used_entries is None:

        for entry in keys:
            key = entry
            value = sorted_totals[key]
            top_5_result[key] = value
    else:

        for entry in used_entries:
            key = keys[entry]
            value = sorted_totals[key]
            top_5_result[key] = value
    return top_5_result


def get_clusters(sequences, labels):
    cluster_0 = []
    cluster_1 = []

    for seq, label in zip(sequences, labels):

        if label == 0:
            cluster_0.append(seq)
        elif label == 1:
            cluster_1.append(seq)
        else:
            raise ValueError("Unknown cluster index= {0}".format(label))

    return cluster_0, cluster_1


def count_kmer_in_repeats(cluster, k, kmer_str):
    """
    Count how many times the kmer_str occurs in the
    sequences in the cluster
    """

    seq_kmers_cluster = {}
    total_counter = 0

    for seq in cluster:

        # get kmers for sequence
        kmers = count_kmers(sequence=seq, k=k)

        if len(kmers) != 0:

            if kmer_str in kmers:
                total_counter += 1

    return  total_counter




if __name__ == '__main__':

    INPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    INPUT_FILE = "deletion_repeats_probability_counts_vectors.csv"
    #INPUT_FILE = "random_deletion_repeats_probability_counts_vectors.csv"
    #INPUT_FILE = "tuf_repeats_probability_counts_vectors.csv"
    #INPUT_FILE  = "normal_repeats_probability_counts_vectors.csv"
    OUTPUT_FILE = "clustering_normal_repeats_probability_counts_vectors.csv"
    OUTPUT_KMERS_FILE = "clustering_normal_repeats_kmers.csv"
    USED_KMERS = []
    USE_ENTRIES = [] #[-1, -2, 3, -4, -5] #-i for i in range(1, 100)]
    K = 4
    MAX_X_LIMIT = 0.35
    DO_PLOT = False
    KMER_STR = 'TCCC'

    EXTRA_INPUT_FILE_1 =  "tuf_repeats_probability_counts_vectors.csv"
    EXTRA_INPUT_FILE_2 = "extracted_deletion_repeats_probability_counts_vectors.csv" #"tuf_repeats_probability_counts_vectors.csv" #"normal_repeats_probability_counts_vectors.csv"


    print("Using input file: {0}".format(INPUT_FILE))

    sequences, vectors = get_data(data_dir=INPUT_DIR, data_file=INPUT_FILE)
    labels = apply_clustering_app_main(data=vectors, n_clusters=1)

    cluster_0, _ = get_clusters(sequences=sequences, labels=labels)

    tccc_kmer_count = count_kmer_in_repeats(cluster=cluster_0, k=K, kmer_str=KMER_STR)

    print("Percentage of {0}={1}".format(KMER_STR, tccc_kmer_count/len(cluster_0)))

    # get the kmers from the cluster
    # if used_kmers == [] this will return
    # all the kmers
    seq_kmers_cluster_0, total_counter_0 = get_cluster_kmers(cluster=cluster_0, used_kmers=USED_KMERS, k=K)
    print("Total counter: ", total_counter_0)

    # calculate the frequency of the kmers
    total_kmers_frequency_0 = get_kmers_frequency(seq_kmers_cluster=seq_kmers_cluster_0)

    # get the sorted top results
    # if use_entries = [] then this returns
    # all the kmers
    top_kmers_result_0 = get_sorted_totals(total_kmers=total_kmers_frequency_0, used_entries=USE_ENTRIES)

    sorted_top_kmers_result_0 = {k: v for k, v in sorted(top_kmers_result_0.items(), key=lambda item: item[0])}
    top_kmers_result_0 = sorted_top_kmers_result_0

    for item in top_kmers_result_0:
        top_kmers_result_0[item] = top_kmers_result_0[item] / total_counter_0


    if 'TCCC' in top_kmers_result_0:
        print("Percentage of TCCC in kmers {0}".format(top_kmers_result_0['TCCC']))
    else:
        print('TCCC is not in kmers')

    if 'GGGA' in top_kmers_result_0:
        print("Percentage of GGGA in kmers {0}".format(top_kmers_result_0['GGGA']))
    else:
        print('GGGA is not in kmers')



    """
    extra_sequences_1, vectors_1 = get_data(data_dir=INPUT_DIR, data_file=EXTRA_INPUT_FILE_1)
    labels1 = apply_clustering_app_main(data=vectors_1, n_clusters=1)

    cluster_0 = []
    cluster_1 = []

    for seq, label in zip(extra_sequences_1, labels1):

        if label == 0:
            cluster_0.append(seq)
        elif label == 1:
            cluster_1.append(seq)
        else:
            raise ValueError("Unknown cluster index= {0}".format(label))

    seq_kmers_cluster_1, total_counter_1 = get_cluster_kmers(cluster=cluster_0, used_kmers=USED_KMERS, k=K)
    total_kmers_1 = get_kmers_frequency(seq_kmers_cluster=seq_kmers_cluster_1)
    top_5_result_1 = get_sorted_totals(total_kmers=total_kmers_1, used_entries=USE_ENTRIES)

    for item in top_5_result_1:
        if item not in top_5_result_0:
            top_5_result_0[item] = 0.0

    extra_sequences_2, vectors_2 = get_data(data_dir=INPUT_DIR, data_file=EXTRA_INPUT_FILE_2)
    labels2 = apply_clustering_app_main(data=vectors_2, n_clusters=1)

    cluster_0 = []
    cluster_1 = []

    for seq, label in zip(extra_sequences_2, labels2):

        if label == 0:
            cluster_0.append(seq)
        elif label == 1:
            cluster_1.append(seq)
        else:
            raise ValueError("Unknown cluster index= {0}".format(label))

    seq_kmers_cluster_2, total_counter_2 = get_cluster_kmers(cluster=cluster_0, used_kmers=USED_KMERS, k=K)
    total_kmers_2 = get_kmers_frequency(seq_kmers_cluster=seq_kmers_cluster_2)
    top_5_result_2 = get_sorted_totals(total_kmers=total_kmers_2, used_entries=USE_ENTRIES)

    for item in top_5_result_2:
        if item not in top_5_result_0:
            top_5_result_0[item] = 0.0

    sorted_top_5_result_0 = {k: v for k, v in sorted(top_5_result_0.items(), key=lambda item: item[0])}
    top_5_result_0 = sorted_top_5_result_0

    """

    if DO_PLOT:
        df = pnd.DataFrame(data={"Kmer": top_kmers_result_0.keys(),
                                 "Kmer Percentage": top_kmers_result_0.values()})

        colors = sns.color_palette()  # sns.color_palette("rocket")
        ax = sns.barplot(x="Kmer Percentage", y="Kmer", data=df, palette=colors)
        ax.set_ylabel("Kmer", fontsize=6)
        ax.tick_params(labelsize=4)
        plt.xlim(0, MAX_X_LIMIT)
        plt.show()


    df = pnd.DataFrame(data={"Kmer": ['DEL_TCCC', 'DEL_GGGA', 'R_DEL_TCCC', 'R_DEL_GGGA',
                                      'TUF_TCCC', 'TUF_GGGA', 'N_TCCC', 'N_GGGA'],
                             "Percenatge of sequences": [0.312, 0.266, 0.080, 0.120, 0.223, 0.197, 0.123, 0.076]})

    colors = sns.color_palette()  # sns.color_palette("rocket")
    ax = sns.barplot(x="Percenatge of sequences", y="Kmer", data=df, palette=colors)
    ax.set_ylabel("Kmer", fontsize=10)
    ax.tick_params(labelsize=10)
    plt.xlim(0, MAX_X_LIMIT)
    plt.show()


    # resort
    #sorted_top_5_result_0 = {k: v for k, v in sorted(top_5_result_0.items(), key=lambda item: item[0])}
    #top_5_result_0 = sorted_top_5_result_0

    """
    seq_kmers_cluster_1 = get_cluster_kmers(cluster=cluster_1)
    total_kmers_1, total_counter_1 = total_kmers(seq_kmers_cluster=seq_kmers_cluster_1)
    top_5_result_1 = get_sorted_totals(total_kmers=total_kmers_1, used_entries=USE_ENTRIES)

    sorted_top_5_result_1 = {k: v for k, v in sorted(top_5_result_1.items(), key=lambda item: item[0])}
    top_5_result_1 = sorted_top_5_result_1

    for item in top_5_result_1:

        # scale the top results for cluster 1
        top_5_result_1[item] = top_5_result_1[item]/total_counter_1

        if item in total_kmers_0:
            if item not in top_5_result_0:
                top_5_result_0[item] = total_kmers_0[item]/total_counter_0
            else:
                # keep what we already have
                pass
        else:
            top_5_result_0[item] = 0/total_counter_0

    # resort
    sorted_top_5_result_0 = {k: v for k, v in sorted(top_5_result_0.items(), key=lambda item: item[0])}
    top_5_result_0 = sorted_top_5_result_0


    for item in top_5_result_0_deep_copy:

        if item in total_kmers_1:

            if item not in top_5_result_1:
                top_5_result_1[item] = total_kmers_1[item]/total_counter_1
            else:
                pass
        else:
            top_5_result_1[item] = 0/total_counter_1

    sorted_top_5_result_1 = {k: v for k, v in sorted(top_5_result_1.items(), key=lambda item: item[0])}
    top_5_result_1 = sorted_top_5_result_1
    """




    """
    df = pnd.DataFrame(data={"Kmer": top_5_result_1.keys(),
                             "Kmer Percentage": top_5_result_1.values()})

    ax = sns.barplot(x="Kmer", y="Kmer Percentage", data=df)
    plt.show()
    """

    #save_kmers(output_dir=INPUT_DIR, output_file=OUTPUT_KMERS_FILE,
    #           seq_kmers_cluster_0=seq_kmers_cluster_0, seq_kmers_cluster_1=seq_kmers_cluster_1)

    #save_clusters(output_dir=INPUT_DIR, output_file=OUTPUT_FILE,
    #              sequences=sequences, labels=labels)


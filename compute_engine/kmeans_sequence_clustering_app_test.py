import csv
import numpy as np
import matplotlib.pyplot as plt

from compute_engine.src.m_kmeans import MbKMeans
from compute_engine.src.cpf import CPF
from compute_engine.src.cpf import collect_words
from compute_engine.src.cpf import reverse_complement


class L2Norm(object):

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return np.linalg.norm(args[0] - args[1])


if __name__ == '__main__':

    seqs = ["CGCCCCTGCCCTGGAGGCCC", "CGCCCCTGCCCTGGAGGCCC" + "CGCCCCTGCCCTGGAGGCCC",
            "GCCCT", ]

    w1 = collect_words(seq=seqs[0], k=2)
    w2 = collect_words(seq=seqs[2], k=2)

    print(w1)
    print("\n")
    print(w2)

    cpf = CPF()
    cpf.add_feature_vector(seq=seqs[0])
    cpf.add_feature_vector(seq=seqs[1])
    cpf.add_feature_vector(seq=seqs[2])

    print(cpf.get_feature_vectors()[0])
    print("\n")
    print(cpf.get_feature_vectors()[1])
    print("\n")
    print(cpf.get_feature_vectors()[2])

    #seqs = ['ATGGTGCACCTGACT', reverse_complement('ATGGTGCACCTGACT')]

    #kmeans = MbKMeans(distance_metric=CPF(), iterations=10, tolerance=1.0e-5,
    #                  n_clusters=2, initializer=None)

    #kmeans.cluster(dataset=seqs)

    """
    data_path = "/home/alex/MySoftware/kmeans/kmeans/demo/data.txt"
    data = np.empty((0, 2), np.float)
    with open(data_path, 'r') as fh:

        reader = csv.reader(fh, delimiter=' ')

        for line in reader:

            if line[0] == '#':
                continue
            x = float(line[1])
            y = float(line[2])
            row = np.array([[x, y]])
            data = np.append(data, row, axis=0)

    kmeans = MbKMeans(distance_metric=L2Norm(), iterations=10, tolerance=1.0e-5,
                      n_clusters=5, initializer=None,
                      use_largest_cluster_to_bisect=False,
                      verbose=True, n_bisection_iterations=1, use_sklearn_kmeans=True)

    kmeans.cluster(dataset=data)

    clusters = kmeans.clusters

    colors = ['ro', 'bo', 'yo', 'go', 'mo', 'ko']
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







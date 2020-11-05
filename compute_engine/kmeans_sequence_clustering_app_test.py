import csv
import numpy as np
import matplotlib.pyplot as plt

from compute_engine.src.m_kmeans import MbKMeans
from compute_engine.src.cpf import CPF
from compute_engine.src.cpf import reverse_complement


class L2Norm(object):

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return np.linalg.norm(args[0] - args[1])

if __name__ == '__main__':
    seqs = ['ATGGTGCACCTGACT', reverse_complement('ATGGTGCACCTGACT')]

    kmeans = MbKMeans(distance_metric=CPF(), iterations=10, tolerance=1.0e-5,
                      n_clusters=2, initializer=None)

    #kmeans.cluster(dataset=seqs)

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
                      verbose=True, n_bisection_itrs=1)

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







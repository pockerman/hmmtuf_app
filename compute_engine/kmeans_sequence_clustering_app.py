from compute_engine.src.m_kmeans import Cluster
from compute_engine.src.m_kmeans import MbKMeans
from compute_engine.src.cpf import CPF
from compute_engine.src.cpf import reverse_complement

if __name__ == '__main__':
    seqs = ['ATGGTGCACCTGACT', reverse_complement('ATGGTGCACCTGACT')]

    kmeans = MbKMeans(distance_metric=CPF(), iterations=10, tolerance=1.0e-5,
                      n_clusters=3, initializer=None)

    kmeans.cluster(dataset=seqs)
"""
Implementation of the modified bisection
k-means algorithm discussed in
A novel hierarchical clustering algorithm for gene
sequences by Wei et all
"""

from compute_engine.src.constants import INFO


class Cluster(object):

    def __init__(self, idx, centroid, indexes=None):
        self._idx = idx
        self._centroid = centroid
        self._indexes = indexes

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, value):
        self._idx = value

    @property
    def centroid(self):
        return self._centroid

    @centroid.setter
    def centroid(self, value):
        self._centroid = value

    @property
    def indexes(self):
        return self._indexes

    @indexes.setter
    def indexes(self, value):
        self._indexes = value

    def compute_variance(self, distance_metric, dataset):

        sum = 0.0
        for index in self._indexes:
            seq = dataset[index]
            dist = distance_metric(seq, self._centroid)
            sum += dist**2
        return sum/len(self._indexes)


class MbKMeans(object):

    def __init__(self, distance_metric, iterations,
                 tolerance, n_clusters, initializer):
        self._distance_metric = distance_metric
        self._iterations = iterations
        self._tolerance = tolerance
        self._n_clusters = n_clusters
        self._initializer = initializer
        self._clusters = []

    def cluster(self, dataset):

        # create the first cluster
        # no centroid is chosen here. This is set up during
        # the first subclustering
        init_cluster = Cluster(idx=0, centroid=None, indexes=[idx for idx in range(len(dataset))])
        self._clusters.append(init_cluster)

        itr = 0
        while len(self._clusters) != self._n_clusters and itr != self._iterations:

            print("{0} At iteration {1} number of clusters {2}".format(INFO, itr, len(self._clusters)))

            # pick a cluster to split
            cluster = self._select_cluster_to_split(dataset=dataset)
            self._sub_cluster(cluster=cluster, dataset=dataset)

            itr += 1

    def _sub_cluster(self, cluster, dataset):
        """
        subcluster the given cluster. Repeatedly divides
        the given cluster until the cluster centroid change is
        less than self._tolerance
        """

        current_indexes = cluster.indexes

        # select two initial centroids from the cluster
        init_centroids = self._select_new_centroids(indices=current_indexes,
                                                    dataset=dataset)

        indexes1 = []
        indexes2 = []

        old_centroid = cluster.centroid
        centroid_changed = True
        while centroid_changed:

            for seq_id in current_indexes:
                seq = dataset[seq_id]

                # to which new centroid is this closer
                dist1 = self._distance_metric(seq, dataset[init_centroids[0]])
                dist2 = self._distance_metric(seq, dataset[init_centroids[1]])

                if dist1 < dist2:
                    indexes1.append(seq_id)
                else:
                    indexes2.append(seq_id)

            if old_centroid is not None and self._distance_metric(old_centroid, dataset[init_centroids[0]]) < self._tolerance:
                centroid_changed = False
            else:

                # update the current cluster
                # indexes and centroid
                cluster.indexes = indexes1
                cluster.centroid = dataset[init_centroids[0]]

                # what happens if the centroids already exist?
                new_cluster = Cluster(idx=len(self._clusters),
                                      centroid=dataset[init_centroids[1]],
                                      indexes=indexes2)
                self._clusters.append(new_cluster)
                old_centroid = cluster.centroid

    def _select_cluster_to_split(self, dataset):

        if len(self._clusters) == 0:
            raise ValueError("Empty clusters")

        if len(self._clusters) == 1:
            return self._clusters[0]

        cluster_idx = -1
        cluster_variance = 0.0

        for cluster in self._clusters:

            var = cluster.compute_variance(distance_metric=self._distance_metric,
                                           dataset=dataset)

            if var > cluster_variance:
                cluster_variance = var
                cluster_idx = cluster.idx

        if cluster_idx < 0:
            raise ValueError("Invalid cluster index")

        return self._clusters[cluster_idx]

    def _select_new_centroids(self, indices, dataset):

        idx_seq1 = -1
        idx_seq2 = -1
        max_dist = 0.0

        # compute the distance pairs
        for idx1 in indices:
            for idx2 in indices:

                if idx1 != idx2:
                    sq1 = dataset[idx1]
                    sq2 = dataset[idx2]
                    dist = self._distance_metric(sq1, sq2)

                    if dist > max_dist:
                        max_dist = dist
                        idx_seq1 = idx1
                        idx_seq2 = idx2
        return idx_seq1, idx_seq2, max_dist
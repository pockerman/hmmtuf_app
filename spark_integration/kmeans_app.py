from compute_engine.src.constants import INFO
from spark_integration.spark_manager import SparkManager
from spark_integration.spark_tasks import compute_sequences_dataframe
from pyspark.ml.clustering import BisectingKMeans


if __name__ == '__main__':

    APP_NAME = "KMeansApp"
    print("{0} Running {1} application".format(INFO, APP_NAME))

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "distances.txt"

    manager = SparkManager(master_url="local", app_name=APP_NAME)

    file_dir = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/data/chr1_repeats/"
    filenames = "region_1/nucl_out.bed"

    sequences_data_frame=compute_sequences_dataframe(spark_manager=manager,
                                                     bedfilename=file_dir+filenames)

    bkm = BisectingKMeans(featuresCol="feature_vector", k=3, minDivisibleClusterSize=10.0)

    # compute the model
    model = bkm.fit(sequences_data_frame)

    # Evaluate clustering.
    cost = model.computeCost(sequences_data_frame)
    print("{0} Within Set SSE={1}".format(INFO, cost))

    print("{0} Printing cluster centers...".format(INFO))
    centers = model.clusterCenters()
    for i, center in enumerate(centers):
        print("{0} cluster {1} has center {2}".format(INFO, i, center))


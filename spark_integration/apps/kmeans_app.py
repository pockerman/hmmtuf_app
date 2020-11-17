from compute_engine.src.constants import INFO
from spark_integration.spark_manager import SparkManager
from spark_integration.spark_tasks import compute_sequences_dataframe
from pyspark.ml.clustering import BisectingKMeans


if __name__ == '__main__':

    APP_NAME = "KMeansApp"
    print("{0} Running {1} application".format(INFO, APP_NAME))

    OUTPUT_DIR = "/computations/sequence_clusters/output/"
    OUTPUT_FILE = "distances.txt"

    manager = SparkManager(master_url="local", app_name=APP_NAME)

    file_dir = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    filenames = "sequences.csv"

    options = dict()
    options["filename"] = file_dir + filenames
    options["cut_sequences_to_min"] = False
    sequences_data_frame = compute_sequences_dataframe(spark_manager=manager, **options)

    sequences_data_frame.summary("min", "max").show()
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


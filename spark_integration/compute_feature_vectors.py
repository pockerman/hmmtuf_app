from compute_engine.src.constants import INFO
from spark_integration.spark_manager import SparkManager
from spark_integration.spark_tasks import compute_feature_vectors_task


if __name__ == '__main__':

    APP_NAME = "ComputeFeaturesApp"
    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "distances.txt"
    print("{0} Running {1} application".format(INFO, APP_NAME))
    manager = SparkManager(master_url="local", app_name=APP_NAME)

    file_dir = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/data/chr1_repeats/"
    filenames = "region_1/nucl_out.bed"

    feature_vectors = compute_feature_vectors_task(spark_manager=manager, bedfilename=file_dir+filenames)
    print("{0} Finished ....".format(INFO))

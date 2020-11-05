from compute_engine.src.constants import INFO
from spark_integration.spark_manager import SparkManager

if __name__ == '__main__':

    APP_NAME = "SparkReadFile"
    print("{0} Running {1} application".format(INFO, APP_NAME))
    manager = SparkManager(master_url="local", app_name=APP_NAME)

    file_dir = "/computations/sequence_clusters/data/chr1_repeats/"
    filenames = "region_1/nucl_out.bed"

    bed_rdd = manager.sc.textFile(file_dir + filenames)
    print("{0} Finished ....".format(INFO))

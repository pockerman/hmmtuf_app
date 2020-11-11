from compute_engine.src.constants import INFO
from compute_engine.src.utils import read_bed_file_line
from compute_engine.src.utils import to_csv_line
from spark_integration.spark_manager import SparkManager

if __name__ == '__main__':

    APP_NAME = "SparkReadFile"
    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "seq_rdd.txt"
    print("{0} Running {1} application".format(INFO, APP_NAME))
    manager = SparkManager(master_url="local", app_name=APP_NAME)

    file_dir = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/data/chr1_repeats/"
    filenames = "region_1/nucl_out.bed"

    # read the bed file
    bed_rdd = manager.sc.textFile(file_dir + filenames)

    # get the RDD containing the lines
    seq_rdd = bed_rdd.map(lambda line: read_bed_file_line(line=line))

    lines = seq_rdd.map(to_csv_line)
    lines.saveAsTextFile(OUTPUT_DIR + OUTPUT_FILE)

    print("{0} Finished ....".format(INFO))

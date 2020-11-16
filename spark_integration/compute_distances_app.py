import numpy as np
from pyspark.sql.functions import lit
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, StructType, StructField, ArrayType, DoubleType
from compute_engine.src.constants import INFO
from compute_engine.src.utils import read_bed_file_line
from compute_engine.src.utils import to_csv_line
from compute_engine.src.cpf import sequence_feature_vector
from spark_integration.spark_manager import SparkManager
from spark_integration.spark_tasks import compute_feature_vectors_task


if __name__ == '__main__':

    APP_NAME = "ComputeDistancesApp"
    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "distances.txt"
    print("{0} Running {1} application".format(INFO, APP_NAME))
    manager = SparkManager(master_url="local", app_name=APP_NAME)

    file_dir = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/data/chr1_repeats/"
    filenames = "region_1/nucl_out.bed"

    feature_vectors = compute_feature_vectors_task(spark_manager=manager, bedfilename=file_dir+filenames)

    # read the bed file
    #bed_rdd = manager.sc.textFile(file_dir + filenames)

    # get the RDD containing the lines
    #seq_rdd = bed_rdd.map(lambda line: read_bed_file_line(line=line))
    #sequences = seq_rdd.map(lambda line: [line[2]])

    # compute
    #feature_vectors = sequences.map(sequence_feature_vector)

    # create a schema
    #schema = StructType([StructField("Sequences", StringType(), True)])

    # get a data frame
    #sequences_data_frame = manager.create_data_frame(rdd=sequences, schema=schema)

    # register user defined function
    #udf_value_to_category = udf(sequence_feature_vector, ArrayType(elementType=DoubleType()))

    # add the features vector column
    #sequences_data_frame = sequences_data_frame.withColumn('FeatureVector', udf_value_to_category("Sequences"))
    #sequences_data_frame.show()



    #cross_product = sequences_data_frame.crossJoin(sequences_data_frame).withColumnRenamed("FeatureVector", "V1")
    #cross_product.show()

    # compute the distances
    #distances = sequences_data_frame.map(lambda pair: np.linalg.norm(np.array(pair[0]) - np.array(pair[1])))

    # compute the feature vectors for every sequence
    #feature_vectors = sequences.map(sequence_feature_vector)

    # take the cartesian product to form pairs
    #cartesian_seqs = feature_vectors.cartesian(feature_vectors)

    # compute distances between the pairs
    #distances = cartesian_seqs.map(lambda pair: np.linalg.norm(np.array(pair[0]) - np.array(pair[1])))

    # map it to CSV to save it
    #lines = distances.map(to_csv_line)
    #lines.saveAsTextFile(OUTPUT_DIR + OUTPUT_FILE)

    print("{0} Finished ....".format(INFO))
import numpy as np

from pyspark.ml.linalg import Vectors
from pyspark.sql.types import StringType, StructType, StructField, ArrayType, DoubleType, IntegerType
from pyspark.sql.functions import udf


from compute_engine.src.cpf import sequence_feature_vector
from compute_engine.src.utils import read_bed_file_line
from compute_engine.src.utils import INFO
from compute_engine.src.utils import to_csv_line
from compute_engine.src.utils import read_sequences_csv_file_line
from compute_engine.src.utils import sequence_length


def compute_feature_vectors_task(spark_manager, bedfilename, as_vectors):

    # read the bed file
    bed_rdd = spark_manager.load_rdd_from_text_file(bedfilename)

    # get the RDD containing the lines
    seq_rdd = bed_rdd.map(lambda line: read_bed_file_line(line=line))

    # extract the sequences
    sequences = seq_rdd.map(lambda line: line[2])

    # compute the feature vectors
    if as_vectors:
        # compute the feature vectors
        feature_vectors_tmp = sequences.map(sequence_feature_vector)

        feature_vectors = feature_vectors_tmp.map(lambda line: Vectors.dense(line))
    else:
        feature_vectors = sequences.map(sequence_feature_vector)

    vectors = feature_vectors.map(lambda item: (item[0], item[1], item[2], item[3],
                                                item[4], item[5], item[6], item[7],
                                                item[8], item[9], item[10], item[11]))

    return vectors


def compute_sequences_dataframe(spark_manager, **options):

    filename = options["filename"]

    rdd = spark_manager.load_rdd_from_text_file(filename)

    # a schema for the data frame
    schema = StructType([StructField("sequence", StringType(), True)])

    if filename.endswith("bed"):
        # get the RDD containing the lines
        seq_rdd = rdd.map(lambda line: read_bed_file_line(line=line))
        # extract the sequences
        sequences = seq_rdd.map(lambda line: [line[2]])
    else:
        seq_rdd = rdd.map(lambda line: read_sequences_csv_file_line(line=line)[1].strip())

        # extract the sequences
        sequences = seq_rdd.map(lambda line: [line])

    sequences_data_frame = spark_manager.create_data_frame(rdd=sequences, schema=schema)

    udf_sequence_to_feature_vector = udf(sequence_feature_vector,
                                         ArrayType(elementType=DoubleType(), containsNull=False))

    sequences_data_frame = sequences_data_frame.withColumn('feature_vector',
                                                           udf_sequence_to_feature_vector("sequence"))

    udf_sequence_length = udf(sequence_length, IntegerType())
    sequences_data_frame = sequences_data_frame.withColumn('length',
                                                           udf_sequence_length("sequence"))

    if "cut_sequences_to_min" in options:
        min_size = seq_rdd.min()
        print("{0} Minimum sequence size {1}".format(INFO, min_size))

    return sequences_data_frame


def compute_distances_task(spark_manager, feature_vectors, save_filename=None):

    # take the cartesian product to form pairs
    cartesian_seqs = feature_vectors.cartesian(feature_vectors)

    # compute the distances
    distances = cartesian_seqs.map(lambda pair: np.linalg.norm(np.array(pair[0]) - np.array(pair[1])))

    if save_filename is not None:
        spark_manager.save_rdd_to_text_file(save_filename, rdd=distances, mapper=to_csv_line)

    return distances




from pyspark import SparkContext
from pyspark.sql import SparkSession

# change the log4j.properties for the changing the
# changing the logging statements


class SparkManager(object):

    @staticmethod
    def save_rdd_to_text_file(filename, rdd, mapper):
        lines = rdd.map(mapper)
        lines.saveAsTextFile(filename)

    def __init__(self, master_url, app_name):
        self._sc = SparkContext(master_url, app_name)
        self._spark_session = SparkSession(self._sc)
        
    @property
    def sc(self):
        return self._sc

    def create_data_frame(self, rdd, schema):
        """
        Create a DataFrame from the given RDD
        """
        return self._spark_session.createDataFrame(rdd, schema=schema)

    def load_rdd_from_text_file(self, filename):
        return self._sc.textFile(filename)



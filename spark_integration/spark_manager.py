from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession

class SparkManager(object):

    def __init__(self, master_url, app_name):
        self._sc = SparkContext(master_url, app_name)
        self._sqlContext = SparkSession(self._sc) #SQLContext(self._sc)
        
    @property
    def sc(self):
        return self._sc

    def create_data_frame(self, rdd, schema):
        """
        Create a DataFrame from the given RDD
        """
        return self._sqlContext.createDataFrame(rdd, schema=schema)

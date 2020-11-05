from pyspark import SparkContext

class SparkManager(object):

    def __init__(self, master_url, app_name):
        self._sc = SparkContext(master_url, app_name)
        #self._sc.addPyFile("/home/alex/qi3/hmmtuf/compute_engine/")

    @property
    def sc(self):
        return self._sc

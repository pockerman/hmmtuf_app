import sqlite3
from sqlite3 import Error


class SQLiteDBConnector(object):

    TABLES = ['distance_metric_type',
              'distance_sequence_type', 'repeats',
              'repeats_distances']

    def __init__(self, db_file):
        self._conn = None
        self._db_file = db_file

    def connect(self):
        """
        Connect the to the DB
        :return:
        """
        try:
            self._conn = sqlite3.connect(self._db_file)
        except Error as e:
            print(str(e))
        return self._conn

    def create_all_tables(self):

        sql_distance_metric_type = "CREATE TABLE IF NOT EXISTS distance_metric_type (type TEXT UNIQUE NOT NULL," \
                                   "short_cut TEXT UNIQUE NOT NULL)"

        self.cursor.execute(sql_distance_metric_type)
        self._conn.commit()

        sql_distance_sequence_type = "CREATE TABLE IF NOT EXISTS distance_sequence_type (type TEXT UNIQUE NOT NULL)"

        self.cursor.execute(sql_distance_sequence_type)
        self._conn.commit()

        sql_repeats = "CREATE TABLE IF NOT EXISTS repeats (type TEXT NOT NULL," \
                      " start_idx INT NOT NULL, end_idx INT NOT NULL," \
                      "repeat_seq TEXT NOT NULL, hmm_state TEXT, " \
                      "gc FLOAT)"

        self.cursor.execute(sql_repeats)
        self._conn.commit()

        sql_repeats_distances = "CREATE TABLE IF NOT EXISTS repeats_distances (chromosome1 TEXT NOT NULL, " \
                                "start_idx_1 INT NOT NULL, " \
                                "end_idx_1 INT NOT NULL, " \
                                "chromosome2 TEXT NOT NULL, " \
                                "start_idx_2 INT NOT NULL, " \
                                "end_idx_2 INT NOT NULL, " \
                                "value FLOAT, " \
                                "metric_type TEXT NOT NULL, sequence_type TEXT NOT NULL, is_normalized INT NOT NULL)"

        self.cursor.execute(sql_repeats_distances)
        self._conn.commit()

    @property
    def cursor(self):
        if self._conn is None:
            raise ValueError("Not Connected to the DB")
        return self._conn.cursor()

    def print_table_column_names(self, table_name):

        sql = "PRAGMA table_info(%s)" % table_name
        self.cursor.execute(sql)
        print(self.cursor.fetchall())

    def fetch_from_distance_metric_type_table_metric(self, metric_type):

        conn = sqlite3.connect(self._db_file)
        cursor = conn.cursor()
        sql = '''SELECT id, type, short_cut from distance_metric_type where type=%s'''%metric_type
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_metric_type_table_by_short_cut(self, short_cut):

        conn = sqlite3.connect(self._db_file)
        cursor = conn.cursor()
        sql = '''SELECT id, type, short_cut from distance_metric_type where short_cut="%s"''' % short_cut
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_metric_type_table_all(self):

        conn = sqlite3.connect(self._db_file)
        sql = '''SELECT * FROM distance_metric_type'''
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows

    def fetch_from_distance_sequence_type_table_by_seq_type(self, seq_type):

        conn = sqlite3.connect(self._db_file)
        cursor = conn.cursor()
        sql = '''SELECT id, type from distance_sequence_type where short_cut="%s"''' % seq_type
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_sequence_type_table_all(self):

        conn = sqlite3.connect(self._db_file)
        cursor = conn.cursor()
        sql = '''SELECT * from distance_sequence_type'''
        cursor.execute(sql)
        return cursor.fetchall()

    def execute(self, sql: str, values: tuple) -> None:
        """
        Execute the sql
        :param sql:
        :param values:
        :return:
        """
        self.cursor.execute(sql, values)
        self._conn.commit()

    def create_table(self, table_name, columns):

        if len(columns) == 0:
            raise ValueError("Empty column names")

        sql = "CREATE TABLE IF NOT EXISTS {0} (".format(table_name)
        sql += "{0}".format(columns[0])

        for col in range(1, len(columns) - 1):
            sql += "{0},".format(columns[col])

        if len(columns) > 1:
            sql += "{0}".format(columns[len(columns) - 1])
        sql += ")"
        self.cursor.execute(sql)
        self._conn.commit()

    def delete_table(self, tbl_name):
        sql = "DROP TABLE IF EXISTS {0};".format(tbl_name)
        self.cursor.execute(sql)
        self._conn.commit()




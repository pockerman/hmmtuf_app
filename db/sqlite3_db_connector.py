import sqlite3
from sqlite3 import Error
from db.db_connector import DBConnectorBase


class SQLiteDBConnector(DBConnectorBase):
    """
    DB connector for SQLite3 database
    """

    def __init__(self, db_file):
        super(SQLiteDBConnector, self).__init__(db_file=db_file)

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

    def delete_all_tables(self, tbl_names: list=None) -> None:
        """
        Delete all the tables in the DB
        """

        if tbl_names is None:
            tbl_names = SQLiteDBConnector.TABLES

        for name in tbl_names:
            self.delete_table(tbl_name=name)

    def create_table(self, table_name: str) -> None:
        """
        Create the table with the given name
        """

        if table_name not in SQLiteDBConnector.TABLES:
            raise ValueError("Invalid table name. Name {0} not in {1}".format(table_name, SQLiteDBConnector.TABLES))

        if table_name == 'distance_metric_type':
            sql = "CREATE TABLE IF NOT EXISTS distance_metric_type " \
                                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                       "type TEXT UNIQUE NOT NULL," \
                                       "short_cut TEXT UNIQUE NOT NULL)"
        elif table_name == 'distance_sequence_type':
            sql = "CREATE TABLE IF NOT EXISTS distance_sequence_type " \
                                     "(id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT UNIQUE NOT NULL)"
        elif table_name == 'repeats':
            sql = "CREATE TABLE IF NOT EXISTS repeats (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                      "chromosome TEXT NOT NULL," \
                      " start_idx INT NOT NULL, end_idx INT NOT NULL," \
                      "repeat_seq TEXT NOT NULL, hmm_state_id INTEGER NOT NULL, " \
                      "gc FLOAT, gc_min FLOAT, gc_max FLOAT, has_gquad INT, has_repeats INT," \
                  "n_repeats INT, align_seq TEXT, unit_seq TEXT)"
        elif table_name == 'repeats_distances':
            sql = "CREATE TABLE IF NOT EXISTS repeats_distances (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                  "repeat_idx_1 INTEGER NOT NULL,  " \
                  "repeat_idx_2 INTEGER NOT NULL, " \
                  "hmm_state_id_1 INTEGER NOT NULL, " \
                  "hmm_state_id_2 INTEGER NOT NULL, " \
                  "value FLOAT, " \
                  "metric_type_id INT NOT NULL, " \
                  "sequence_type_id INT NOT NULL, " \
                  "is_normalized INT NOT NULL)"
        elif table_name == 'hmm_state_types':
            sql = "CREATE TABLE IF NOT EXISTS hmm_state_types(id INTEGER PRIMARY KEY AUTOINCREMENT," \
                  "type TEXT NOT NULL)"

        self.cursor.execute(sql)
        self._conn.commit()

    def create_all_tables(self):
        """
        Create all the tables in the schema
        """
        for name in SQLiteDBConnector.TABLES:
            self.create_table(table_name=name)

    @property
    def cursor(self):
        if self._conn is None:
            raise ValueError("Not Connected to the DB")
        return self._conn.cursor()

    def get_table_column_names(self, table_name: str) -> list:
        """
        Print the column names for the given table
        """

        cursor = self.cursor
        sql = "PRAGMA table_info(%s)" % table_name
        cursor.execute(sql)
        return cursor.fetchall()

    def fetch_from_distance_metric_type_table_by_metric(self, metric_type: str) -> tuple:
        """
        Fetch the metric type corresponding to the given metric_type
        """

        cursor = self.cursor
        sql = '''SELECT id, type, short_cut from distance_metric_type where type="%s"''' % metric_type
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_metric_type_table_by_short_cut(self, short_cut: str) -> tuple:
        """
        Fetch the metric type corresponding to the given short cut
        """

        cursor = self.cursor
        sql = '''SELECT id, type, short_cut from distance_metric_type where short_cut="%s"''' % short_cut
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_metric_type_table_by_id(self, idx: int) -> tuple:
        """
        Fetch the metric type corresponding to the given idx
        """

        cursor = self.cursor
        sql = '''SELECT id, type, short_cut from distance_metric_type where id=%s''' % idx
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_metric_type_table_all(self) -> list:
        """
        Fetch all the metric types
        """

        sql = '''SELECT * FROM distance_metric_type'''
        cursor = self.cursor
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows

    def fetch_from_distance_sequence_type_table_by_seq_type(self, seq_type: str) -> tuple:
        """
        Fetch the sequence type corresponding to the given seq_type
        """

        cursor = self.cursor
        sql = '''SELECT id, type from distance_sequence_type where type="%s"''' % seq_type
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_sequence_type_table_by_id(self, idx: int) -> tuple:
        """
        Fetch the sequence type corresponding to the given idx
        """

        cursor = self.cursor
        sql = '''SELECT id, type from distance_sequence_type where id=%s''' % idx
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_distance_sequence_type_table_all(self) -> list:
        """
        Returns all the rows in the distance_sequence_type table
        """

        cursor = self.cursor
        sql = '''SELECT * from distance_sequence_type'''
        cursor.execute(sql)
        return cursor.fetchall()

    def fetch_from_repeats_table_by_id(self, idx: int) -> tuple :
        """
        Fetch the repeat corresponding to the given idx
        """

        cursor = self.cursor
        sql = '''SELECT * from repeats where id=%s''' % idx
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_repeats_table_by_chromosome(self, chromosome: str) -> list:
        """
        Fetch the repeats from the given chromosome
        """

        cursor = self.cursor
        sql = '''SELECT * from repeats where chromosome="%s"''' % chromosome
        cursor.execute(sql)
        return cursor.fetchall()

    def fetch_from_repeats_table_by_coordinates(self, start_idx: int, end_idx: int) -> list:
        """
        Fetch the repeats with the given [start_idx, end_idx)
        """

        cursor = self.cursor
        sql = '''SELECT * from repeats where start_idx=%s and end_idx=%s''' % (start_idx, end_idx)
        cursor.execute(sql)
        return cursor.fetchall()

    def fetch_from_repeats_table_by_hmm_state(self, hmm_state_id: int) -> list:
        """
        Fetch the repeats with the given HMM state
        """

        cursor = self.cursor
        sql = '''SELECT * from repeats where hmm_state_id=%s''' % hmm_state_id
        cursor.execute(sql)
        return cursor.fetchall()

    def fetch_from_repeats_table_all(self) -> list:
        """
        Fetch all data from the repeats table
        """

        cursor = self.cursor
        sql = '''SELECT * from repeats'''
        cursor.execute(sql)
        return cursor.fetchall()

    def fetch_from_hmm_state_types_by_id(self, idx: int) -> tuple:
        """
        Return the hmm_state_types table tuple
        corresponding from to the id
        """

        cursor = self.cursor
        sql = '''SELECT * from hmm_state_types where id=%s''' % idx
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_hmm_state_types_by_type(self, hmm_type: str) -> tuple:
        """
        Return the hmm_state_types table tuple
        corresponding from to the type
        """

        cursor = self.cursor
        sql = '''SELECT * from hmm_state_types where type="%s"''' % hmm_type
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_from_hmm_state_types_all(self) -> list:
        """
        Return the hmm_state_types
        """

        cursor = self.cursor
        sql = '''SELECT * from hmm_state_types'''
        cursor.execute(sql)
        return cursor.fetchall()

    def fetch_one(self, sql: str) -> tuple:
        """
        Execute the given SQL and fetch one result
        """

        cursor = self.cursor
        cursor.execute(sql)
        return cursor.fetchone()

    def fetch_all(self, sql: str) -> list:
        """
        Execute the given SQL and fetch all results
        """

        cursor = self.cursor
        cursor.execute(sql)
        return cursor.fetchall()

    def execute_transaction(self, data, sql) -> None:

        cursor = self.cursor
        cursor.execute("BEGIN TRANSACTION")

        for item in data:
            cursor.execute(sql, item)

        cursor.execute('COMMIT')

    def execute(self, sql: str, values: tuple) -> None:
        """
        Execute the sql
        """
        self.cursor.execute(sql, values)
        self._conn.commit()

    def execute_sql(self, sql: str) -> None:
        """
        Execute the SQL
        """
        cursor = self.cursor
        cursor.execute(sql)
        self._conn.commit()

    def create_table_from_columns(self, table_name: str, columns: list) -> None:
        """
        Create the table with the given name and the given
        columns. The table is created only if it doesn't exist
        """

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

    def create_tmp_table(self, sql: str) -> None:

        cursor = self.cursor
        cursor.execute(sql)
        self._conn.commit()

    def delete_table(self, tbl_name: str) -> None:
        """
        Delete the table with the given name
        if the table exists
        """

        sql = "DROP TABLE IF EXISTS {0};".format(tbl_name)
        cursor = self.cursor
        cursor.execute(sql)
        self._conn.commit()

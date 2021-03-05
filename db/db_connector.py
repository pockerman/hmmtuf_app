from abc import abstractmethod
import sqlite3
from sqlite3 import Error


class DBConnectorBase(object):

    TABLES = ['distance_metric_type',
              'distance_sequence_type', 'repeats',
              'repeats_distances', 'repeats_info', 'gquads_info']

    @staticmethod
    def get_table_names() -> list:
        """
        Returns the table names the DB has
        """
        return DBConnectorBase.TABLES

    def __init__(self, db_file: str) -> None:
        self._conn = None
        self._db_file = db_file

    @property
    def cursor(self):
        if self._conn is None:
            raise ValueError("Not Connected to the DB")
        return self._conn.cursor()

    @abstractmethod
    def connect(self) -> None:
        """
        Connect the to the DB
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_all_tables(self) -> None:
        """
        Delete all the tables in the DB
        """
        raise NotImplementedError()

    @abstractmethod
    def create_all_tables(self) -> None:
        """
        Create all the DB tables
        """
        raise NotImplementedError()

    @abstractmethod
    def get_table_column_names(self, table_name: str) -> list:
        """
        Returns the column names corresponding to the
        given table name
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_distance_metric_type_table_by_metric(self, metric_type: str) -> tuple:
        """
        Fetch the metric type corresponding to the given metric_type
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_distance_metric_type_table_by_short_cut(self, short_cut: str) -> tuple:
        """
        Fetch the metric type corresponding to the given short cut
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_distance_metric_type_table_by_id(self, idx: int) -> tuple:
        """
        Fetch the metric type corresponding to the given idx
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_distance_metric_type_table_all(self) -> list:
        """
        Fetch all the metric types
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_distance_sequence_type_table_by_seq_type(self, seq_type: str) -> tuple:
        """
        Fetch the sequence type corresponding to the given seq_type
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_distance_sequence_type_table_by_id(self, idx: int) -> tuple:
        """
        Fetch the sequence type corresponding to the given idx
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_distance_sequence_type_table_all(self) -> list:
        """
        Returns all the rows in the distance_sequence_type table
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_table_by_id(self, idx: int) -> tuple:
        """
        Fetch the repeat corresponding to the given idx
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_table_by_chromosome(self, chromosome: str) -> list:
        """
        Fetch the repeats from the given chromosome
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_table_by_coordinates(self, start_idx: int, end_idx: int) -> list:
        """
        Fetch the repeats with the given [start_idx, end_idx)
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_table_by_hmm_state(self, hmm_state: str) -> list:
        """
        Fetch the repeats with the given HMM state
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_table_all(self) -> list:
        """
        Fetch all data from the repeats table
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_info_table_by_id(self, idx: int) -> tuple:
        """
        Fetch the unique entry in the repeats_info table
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_info_table_by_chromosome(self, chromosome: str) -> list:
        """
        Fetch all data in the repeats_info table corresponding to
        the given chromosome
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_repeats_info_table_all(self) -> list:
        """
        Fetch all data in the repeats_info table
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_gquads_info_table_by_id(self, idx: int) -> tuple:
        """
        Fetch the unique entry in the gquads_info table
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_gquads_info_table_by_chromosome(self, chromosome: str) -> list:
        """
        Fetch all data in the gquads_info table corresponding to
        the given chromosome
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_from_gquads_info_table_all(self) -> list:
        """
        Fetch all data in the gquads_info table
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_one(self, sql: str) -> tuple:
        """
        Execute the given SQL and fetch one result
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_all(self, sql: str) -> list:
        """
        Execute the given SQL and fetch all results
        """
        raise NotImplementedError()

    @abstractmethod
    def execute(self, sql: str, values: tuple) -> None:
        """
        Execute the sql
        """
        raise NotImplementedError()

    @abstractmethod
    def create_table(self, table_name: str, columns: list) -> None:
        """
        Create the table with the given name and the given
        columns. The table is create only if it doesn't exist
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_table(self, tbl_name: str) -> None:
        """
        Delete the table with the given name
        if the table exists
        """
        raise NotImplementedError()










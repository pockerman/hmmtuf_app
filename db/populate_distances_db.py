import sqlite3
from sqlite3 import Error
import csv
import os
from pathlib import Path

from compute_engine.src.file_readers import NuclOutFileReader
from db.db_connector import SQLiteDBConnector


def create_distance_types_table(database_wrap: SQLiteDBConnector) -> None:

    #database_wrap.delete_table(tbl_name="distance_type")
    database_wrap.create_table(table_name="distance_sequence_type", columns=["type TEXT NOT NULL UNIQUE"])

    CHOICES = [("NORMAL", "NORMAL"),
               ("PURINE", "PURINE"),
               ("AMINO", "AMINO"),
               ("WEAK_HYDROGEN", "WEAK_HYDROGEN"), ]

    for choice in CHOICES:
        sql = '''INSERT INTO distance_sequence_type(type) values(?)'''
        database_wrap.execute(sql=sql, values=(choice[0],))


def create_distance_metrics_table(database_wrap: SQLiteDBConnector,
                                  metrics: dir) -> None:

    # create the table
    #db.create_table(table_name="distance_metric", columns=["type TEXT NOT NULL UNIQUE"])

    """
    metrics = {'ham': "Hamming", 'mlipns': "MLIPNS",
               'lev': "Levenshtein", 'damlev': "DamerauLevenshtein",
               'jwink': "JaroWinkler", 'str': "StrCmp95",
               'nw': "NeedlemanWunsch", 'got': "Gotoh",
               'jac': "Jaccard", 'sor': "Sorensen",
               'tve': "Tversky", 'ov': "Overlap",
               'tan': "Tanimoto", 'cos': "Cosine",
               'mon': "MongeElkan", 'bag': "Bag", 'lcsseq': "LCSSeq",
               'lcsstr': "LCSStr", 'rat': "RatcliffObershelp",
               'ari': "ArithNCD", 'rle': "RLENCD",
               'bwt': "BWTRLENCD", 'sqr': "SqrtNCD",
               'ent': "EntropyNCD", 'bz2': "BZ2NCD", 'lzm': "LZMANCD",
               'zli': "ZLIBNCD", 'mra': "MRA", 'edi': "Editex",
               'pre': "Prefix", 'pos': "Postfix",
               'len': "Length", 'id': "Identity", 'mat': "Matrix", }
    """

    for met in metrics:
        sql = '''INSERT INTO distance_metric_type(type, short_cut) values(?,?)'''
        values = (metrics[met], met)
        database_wrap.execute(sql=sql, values=values)


def create_repeats_table(database_wrap: SQLiteDBConnector, repeats_file: str) -> None:

    file_reader = NuclOutFileReader(exclude_seqs=["NO_REPEATS"])
    seqs = file_reader(filename=repeats_file)

    for seq in seqs:
        sql = '''INSERT INTO repeats(chromosome, start_idx, end_idx, repeat_seq, hmm_state, gc) values(?,?,?,?,?,?)'''

        seq[-1] = seq[-1].strip()
        seq.append(0.0)
        values = seq
        print(values)
        database_wrap.execute(sql=sql, values=values)


def create_repeats_distances_table(database_wrap: SQLiteDBConnector,
                                   data_dir: Path, metrics: dir) -> None:

    # get all the directories in the path
    data_directories = os.listdir(path=data_dir)
    #print(data_directories)

    database_wrap.print_table_column_names("repeats_distances")

    metric_types = database_wrap.fetch_from_distance_metric_type_table_all()
    sequence_types = database_wrap.fetch_from_distance_sequence_type_table_all()

    squence_types_dict = {}

    for seq_item in sequence_types:
        squence_types_dict[seq_item[1]] = seq_item[0]

    for directory in data_directories:

        directory_path = data_dir / directory
        if os.path.isdir(directory_path):

            short_cut = directory_path.name#.split("/")[-1]
            metric_data = database_wrap.fetch_from_distance_metric_type_table_by_short_cut(short_cut=short_cut)
            metric_type_id = metric_data[0]

            print("Working in results directory {0}".format(directory_path))

            # get all the results directories
            results_dir = os.listdir(path=directory_path)

            for result_dir in results_dir:
                result_dir_path = directory_path / result_dir
                if os.path.isdir(result_dir_path):

                    # for each directory collect .csv files
                    csv_files = os.listdir(path=result_dir_path)

                    for csv_file in csv_files:
                        print(result_dir_path / csv_file)
                        with open(result_dir_path / csv_file, 'r', newline="\n") as fh:
                            reader = csv.reader(fh, delimiter=",")

                            for row in reader:
                                if row[0] == '#':
                                    continue

                                chromosome1 = row[0]
                                start_idx_1 = int(row[1])
                                end_idx_1 = int(row[2])

                                chromosome2 = row[5]
                                start_idx_2 = int(row[6])
                                end_idx_2 = int(row[7])
                                value = float(row[10])
                                is_normalized = 1
                                sequence_type_id = squence_types_dict["NORMAL"]

                                sql = '''INSERT INTO repeats_distances(chromosome1, start_idx_1, 
                                end_idx_1, chromosome2, 
                                start_idx_2, end_idx_2, value, 
                                metric_type_id, sequence_type_id, is_normalized) values(?,?, ?, ?, ?, ?, ?, ?, ?, ?)'''

                                values = (chromosome1, start_idx_1, end_idx_1,
                                          chromosome2, start_idx_2, end_idx_2,
                                          value, metric_type_id, sequence_type_id, is_normalized)

                                database_wrap.execute(sql=sql, values=values)

                                value = float(row[11])
                                sequence_type_id = squence_types_dict["PURINE"]
                                values = (chromosome1, start_idx_1, end_idx_1,
                                          chromosome2, start_idx_2, end_idx_2,
                                          value, metric_type_id, sequence_type_id, is_normalized)

                                database_wrap.execute(sql=sql, values=values)

                                value = float(row[12])
                                sequence_type_id = squence_types_dict["AMINO"]
                                values = (chromosome1, start_idx_1, end_idx_1,
                                          chromosome2, start_idx_2, end_idx_2,
                                          value, metric_type_id, sequence_type_id, is_normalized)

                                database_wrap.execute(sql=sql, values=values)

                                value = float(row[13])
                                sequence_type_id = squence_types_dict["WEAK_HYDROGEN"]
                                values = (chromosome1, start_idx_1, end_idx_1,
                                          chromosome2, start_idx_2, end_idx_2,
                                          value, metric_type_id, sequence_type_id, is_normalized)

                                database_wrap.execute(sql=sql, values=values)


def main(database_wrap: SQLiteDBConnector,
         repeats_file: str, data_dir: Path,
         metrics: dir) -> None:

    #create_distance_types_table(database_wrap=database_wrap)
    #create_distance_metrics_table(database_wrap=database_wrap, metrics=metrics)
    #create_repeats_table(database_wrap=database_wrap, repeats_file=repeats_file)
    create_repeats_distances_table(database_wrap=database_wrap,
                                   data_dir=data_dir, metrics=metrics)


if __name__ == '__main__':

    db_file = "../db.sqlite3"
    repeats_file = "../computations/distances/nucl_out.bed"
    data_dir = Path("../computations/distances/")

    metrics = {'ham': "Hamming", 'mlipns': "MLIPNS",
               'lev': "Levenshtein", 'damlev': "DamerauLevenshtein",
               'jwink': "JaroWinkler", 'str': "StrCmp95",
               'nw': "NeedlemanWunsch", 'got': "Gotoh",
               'jac': "Jaccard", 'sor': "Sorensen",
               'tve': "Tversky", 'ov': "Overlap",
               'tan': "Tanimoto", 'cos': "Cosine",
               'mon': "MongeElkan", 'bag': "Bag", 'lcsseq': "LCSSeq",
               'lcsstr': "LCSStr", 'rat': "RatcliffObershelp",
               'ari': "ArithNCD", 'rle': "RLENCD",
               'bwt': "BWTRLENCD", 'sqr': "SqrtNCD",
               'ent': "EntropyNCD", 'bz2': "BZ2NCD", 'lzm': "LZMANCD",
               'zli': "ZLIBNCD", 'mra': "MRA", 'edi': "Editex",
               'pre': "Prefix", 'pos': "Postfix",
               'len': "Length", 'id': "Identity", 'mat': "Matrix", }

    database_wrap = SQLiteDBConnector(db_file=db_file)
    database_wrap.connect()
    main(database_wrap=database_wrap, repeats_file=repeats_file,
         data_dir=data_dir, metrics=metrics)
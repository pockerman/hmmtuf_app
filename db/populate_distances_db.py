import csv
import os
from pathlib import Path

from compute_engine.src.file_readers import NuclOutFileReader
from compute_engine.src.utils import INFO
from db.sqlite3_db_connector import SQLiteDBConnector


def create_distance_types_table(database_wrap: SQLiteDBConnector) -> None:

    print("{0} Creating table {1}...".format(INFO, "distance_sequence_type"))
    database_wrap.create_table(table_name="distance_sequence_type")

    CHOICES = [("NORMAL", "NORMAL"),
               ("PURINE", "PURINE"),
               ("AMINO", "AMINO"),
               ("WEAK_HYDROGEN", "WEAK_HYDROGEN"), ]

    for choice in CHOICES:
        sql = '''INSERT INTO distance_sequence_type(type) values(?)'''
        database_wrap.execute(sql=sql, values=(choice[0],))

    print("{0} Done...".format(INFO))


def create_hmm_types_table(database_wrap: SQLiteDBConnector) -> None:

    print("{0} Creating table {1}...".format(INFO, "hmm_state_types"))
    database_wrap.create_table(table_name="hmm_state_types")
    choices = ['NORMAL', 'TUF', 'DELETION', 'DUPLICATION']

    for choice in choices:
        sql = '''INSERT INTO hmm_state_types(type) values(?)'''
        database_wrap.execute(sql=sql, values=(choice,))
    print("{0} Done...".format(INFO))


def create_distance_metrics_table(database_wrap: SQLiteDBConnector,
                                  metrics: dir) -> None:

    database_wrap.create_table(table_name="distance_metric_type")
    print("{0} Creating table {1}...".format(INFO, "distance_metric_type"))
    for met in metrics:
        sql = '''INSERT INTO distance_metric_type(type, short_cut) values(?,?)'''
        values = (metrics[met], met)
        database_wrap.execute(sql=sql, values=values)

    print("{0} Done...".format(INFO))


def create_repeats_table(database_wrap: SQLiteDBConnector, repeats_file: Path) -> None:

    #database_wrap.delete_table(tbl_name='repeats')
    database_wrap.create_table(table_name='repeats')

    hmm_states = database_wrap.fetch_from_hmm_state_types_all()

    hmm_state_dict = {}

    for state in hmm_states:
        hmm_state_dict[state[1]] = state[0]

    file_reader = NuclOutFileReader(exclude_seqs=["NO_REPEATS"])
    seqs = file_reader(filename=repeats_file)

    for seq in seqs:
        sql = '''INSERT INTO repeats(chromosome, start_idx, end_idx, repeat_seq, hmm_state_id, gc) values(?,?,?,?,?,?)'''

        seq[-1] = seq[-1].strip()
        seq[-1] = seq[-1].upper()
        seq[-1] = hmm_state_dict[seq[-1]]
        seq.append(0.0)
        values = seq
        database_wrap.execute(sql=sql, values=values)


def create_repeats_info_table(database_wrap: SQLiteDBConnector, data_dir: Path, delimiter="\t") -> None:

    database_wrap.create_table(table_name="repeats_info")
    data_directories = os.listdir(path=data_dir)

    for directory in data_directories:
        directory_path = data_dir / directory

        if directory_path.is_dir():
            # this is a directory so do work
            tmp_path = directory_path / directory / 'repeates_info_file.bed'
            with open(tmp_path, 'r', newline="\n") as fh:

                for line in fh:
                    line = line.split(delimiter)
                    chromosome = line[0].strip()
                    start_idx = int(line[1].strip())
                    end_idx = int(line[2].strip())
                    max_repeats_count = int(line[3].strip())
                    align_seq = line[4].strip().upper()
                    unit_seq = line[5].strip().upper()

                    sql = '''INSERT INTO repeats_info(chromosome, 
                    start_idx, end_idx,  max_repeats_count, 
                    align_seq,  unit_seq) values(?, ?, ?, ?, ?, ?)'''
                    values = (chromosome, start_idx, end_idx, max_repeats_count, align_seq, unit_seq)
                    database_wrap.execute(sql=sql, values=values)


def create_gquads_info_table(database_wrap: SQLiteDBConnector, data_dir: Path, delimiter="\t") -> None:

    database_wrap.create_table(table_name="gquads_info")
    data_directories = os.listdir(path=data_dir)

    for directory in data_directories:
        directory_path = data_dir / directory

        if directory_path.is_dir():
            # this is a directory so do work
            tmp_path = directory_path / directory / 'gquads.txt'
            with open(tmp_path, 'r', newline="\n") as fh:

                for line in fh:
                    line = line.split(delimiter)
                    part_one = line[0]
                    part_one_split = part_one.split(":")
                    chromosome = part_one_split[0].strip()

                    part_one_split = part_one_split[1].split('-')

                    start_idx = int(part_one_split[0].strip())

                    part_one_two_split = part_one_split[1].split('_')

                    end_idx = int(part_one_two_split[0].strip())
                    average_gc_count = float(part_one_two_split[2].strip())

                    if part_one_two_split[3].strip() != 'NA':
                        min_gc_count = float(part_one_two_split[3].strip())
                    else:
                        min_gc_count = None

                    if part_one_two_split[4].strip() != 'NA':
                        max_gc_count = float(part_one_two_split[4].strip())
                    else:
                        max_gc_count = None

                    sql = '''INSERT INTO gquads_info(chromosome, 
                        start_idx, end_idx,  average_gc_count, 
                        min_gc_count,  max_gc_count) values(?, ?, ?, ?, ?, ?)'''
                    values = (chromosome, start_idx, end_idx, average_gc_count, min_gc_count, max_gc_count)
                    database_wrap.execute(sql=sql, values=values)


def insert_distance_metric_result(database_wrap: SQLiteDBConnector,
                                  directory_path: Path, metric_data: tuple,
                                  batch_size=2000) -> None:

    print("{0} Inserting metric {1}".format(INFO, metric_data[1]))

    sequence_types = database_wrap.fetch_from_distance_sequence_type_table_all()
    squence_types_dict = {}

    for seq_item in sequence_types:
        squence_types_dict[seq_item[1]] = seq_item[0]

    metric_type_id = metric_data[0]

    # get all the results directories
    results_dir = os.listdir(path=directory_path)

    for result_dir in results_dir:
        result_dir_path = directory_path / result_dir

        if os.path.isdir(result_dir_path):

            # for each directory collect .csv files
            csv_files = os.listdir(path=result_dir_path)

            for csv_file in csv_files:

                if csv_file.endswith('.csv'):

                    print("{0} Working with file {1}".format(INFO, result_dir_path / csv_file))

                    with open(result_dir_path / csv_file, 'r', newline="\n") as fh:

                        reader = csv.reader(fh, delimiter=",")
                        batch_data = []

                        sql = '''INSERT INTO repeats_distances(chromosome1, start_idx_1, 
                                                end_idx_1, chromosome2, 
                                                start_idx_2, end_idx_2, value, 
                                                metric_type_id, sequence_type_id, is_normalized) values(?,?, ?, ?, ?, ?, ?, ?, ?, ?)'''

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

                            values = (chromosome1, start_idx_1, end_idx_1,
                                      chromosome2, start_idx_2, end_idx_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)

                            #database_wrap.execute(sql=sql, values=values)

                            value = float(row[11])
                            sequence_type_id = squence_types_dict["PURINE"]
                            values = (chromosome1, start_idx_1, end_idx_1,
                                      chromosome2, start_idx_2, end_idx_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)
                            #database_wrap.execute(sql=sql, values=values)

                            value = float(row[12])
                            sequence_type_id = squence_types_dict["AMINO"]
                            values = (chromosome1, start_idx_1, end_idx_1,
                                      chromosome2, start_idx_2, end_idx_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)
                            #database_wrap.execute(sql=sql, values=values)

                            value = float(row[13])
                            sequence_type_id = squence_types_dict["WEAK_HYDROGEN"]
                            values = (chromosome1, start_idx_1, end_idx_1,
                                      chromosome2, start_idx_2, end_idx_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)
                            #database_wrap.execute(sql=sql, values=values)

                            if len(batch_data) >= batch_size:
                                database_wrap.execute_transaction(data=batch_data, sql=sql)
                                batch_data = []

                        if len(batch_data) != 0:
                            database_wrap.execute_transaction(data=batch_data, sql=sql)
                            batch_data = []
    print("{0} Inserting metric {1}".format(INFO, metric_data[1]))


def create_repeats_distances_table(database_wrap: SQLiteDBConnector,
                                   data_dir: Path, metrics: dir) -> None:

    """
    Populate the repeats_distances table
    """

    if len(metrics) == 0:
        print("{0} Metrics map is empty exiting...".format(INFO))

    # get all the directories in the path
    # data_directories = os.listdir(path=data_dir)

    database_wrap.create_table(table_name="repeats_distances")
    #database_wrap.execute_sql(sql="DELETE FROM repeats_distances WHERE metric_type_id=3")

    for metric in metrics:
        directory_path = data_dir / metric

        if os.path.isdir(directory_path):

            short_cut = metric

            if short_cut in metrics:
                metric_data = database_wrap.fetch_from_distance_metric_type_table_by_short_cut(short_cut=short_cut)

                insert_distance_metric_result(database_wrap=database_wrap,
                                              metric_data=metric_data,
                                              directory_path=directory_path)


def main(database_wrap: SQLiteDBConnector,
         repeats_file: Path,
         data_dir: Path,
         chromosomes_dir: Path,
         metrics: dir) -> None:

    database_wrap.delete_all_tables()
    #database_wrap.create_all_tables()

    create_hmm_types_table(database_wrap=database_wrap)
    create_distance_types_table(database_wrap=database_wrap)
    create_distance_metrics_table(database_wrap=database_wrap, metrics=metrics)
    create_repeats_table(database_wrap=database_wrap, repeats_file=repeats_file)
    create_repeats_info_table(database_wrap=database_wrap, data_dir=chromosomes_dir)
    create_gquads_info_table(database_wrap=database_wrap, data_dir=chromosomes_dir)
    create_repeats_distances_table(database_wrap=database_wrap,
                                   data_dir=data_dir, metrics=metrics)


if __name__ == '__main__':

    db_file = "/home/alex/qi3/hmmtuf/play_ground.sqlite3"
    repeats_file = Path("/home/alex/qi3/hmmtuf/computations/distances/nucl_out.bed")
    data_dir = Path("/home/alex/qi3/hmmtuf/computations/distances/")
    chromosomes_dir = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/")

    """
    metrics = {'ham': "Hamming", 'mlipns': "MLIPNS",
               'lev': "Levenshtein", 'damlev': "DamerauLevenshtein",
               'jwink': "JaroWinkler", 'str': "StrCmp95",
               'nw': "NeedlemanWunsch",
               'sw': "SmithWaterman",
               'got': "Gotoh",
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
    metrics = {'sw': "SmithWaterman"} #, 'sor': "Sorensen", }

    database_wrap = SQLiteDBConnector(db_file=db_file)
    database_wrap.connect()
    main(database_wrap=database_wrap, repeats_file=repeats_file,
         chromosomes_dir=chromosomes_dir,
         data_dir=data_dir, metrics=metrics)

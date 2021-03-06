import csv
import os
from pathlib import Path

from compute_engine.src.file_readers import NuclOutFileReader, CsvFileReader
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


def create_distance_metrics_table(database_wrap: SQLiteDBConnector, metrics: dir) -> None:

    print("{0} Creating table {1}...".format(INFO, "distance_metric_type"))
    database_wrap.create_table(table_name="distance_metric_type")

    for met in metrics:
        sql = '''INSERT INTO distance_metric_type(type, short_cut) values(?,?)'''
        values = (metrics[met], met)
        database_wrap.execute(sql=sql, values=values)

    print("{0} Done...".format(INFO))


def create_repeats_table(database_wrap: SQLiteDBConnector, repeats_file: Path) -> None:

    print("{0} Creating table repeats...".format(INFO))
    database_wrap.create_table(table_name='repeats')

    hmm_states = database_wrap.fetch_from_hmm_state_types_all()

    hmm_state_dict = {}

    for state in hmm_states:
        hmm_state_dict[state[1]] = state[0]

    file_reader = CsvFileReader()
    seqs = file_reader(filename=repeats_file)

    for seq in seqs:
        chromosome = str(seq[0].strip())
        start_idx = int(seq[1])
        end_idx = int(seq[2])
        repeat = str(seq[3].strip())
        state = str(seq[4].strip()).upper()
        hmm_state_id = hmm_state_dict[state]
        gc = float(seq[5])
        gc_min = float(seq[6])
        gc_max = float(seq[7])
        has_repeats = 0
        if seq[8] == 'True':
            has_repeats = 1

        n_repeats = int(seq[9])
        align_seq = str(seq[10])
        unit_seq = str(seq[11])

        #sql = '''SELECT * FROM repeats WHERE chromosome='%s' AND start_idx=%s AND
        #end_idx=%s AND repeat_seq='%s' ''' % (seq[0], seq[1], seq[2], seq[3])

        #rows = database_wrap.fetch_all(sql=sql)

        #if len(rows) == 0:

        sql = '''INSERT INTO repeats(chromosome, start_idx, end_idx, repeat_seq, 
            hmm_state_id, gc, gc_min, gc_max, has_repeats, n_repeats, align_seq, unit_seq) values(?,?,?,?,?,?,?,?,?,?,?,?)'''

        values = (chromosome, start_idx, end_idx, repeat, hmm_state_id,
                  gc, gc_min, gc_max, has_repeats, n_repeats, align_seq, unit_seq)
        database_wrap.execute(sql=sql, values=values)
    print("{0} Done...".format(INFO))


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

    sql_repeats = '''SELECT id, hmm_state_id, chromosome, start_idx, end_idx, repeat_seq FROM repeats'''

    repeats_rows = database_wrap.fetch_all(sql=sql_repeats)
    repeats_map = {}
    for item in repeats_rows:
        key = (item[2], item[3], item[4], item[5])
        value = (item[0], item[1])

        if key in repeats_rows:
            raise ValueError("Repeat {0} already encountered".format(key))

        repeats_map[key] = value

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

                        insert_sql = '''INSERT INTO repeats_distances(repeat_idx_1, repeat_idx_2,  
                        hmm_state_id_1, hmm_state_id_2, value, 
                        metric_type_id, sequence_type_id, is_normalized) values(?, ?, ?, ?, ?, ?, ?, ?)'''

                        for row in reader:
                            if row[0] == '#':
                                continue

                            chromosome1 = row[0]
                            start_idx_1 = int(row[1])
                            end_idx_1 = int(row[2])
                            seq = row[3]

                            repeat_idx_1, hmm_state_id_1 = repeats_map[(chromosome1, start_idx_1, end_idx_1, seq)]

                            chromosome2 = row[5]
                            start_idx_2 = int(row[6])
                            end_idx_2 = int(row[7])
                            seq = row[8]

                            repeat_idx_2, hmm_state_id_2 = repeats_map[(chromosome2, start_idx_2, end_idx_2, seq)]

                            # don't add self distancing
                            if repeat_idx_1 == repeat_idx_2:
                                continue

                            value = float(row[10])
                            is_normalized = 1
                            sequence_type_id = squence_types_dict["NORMAL"]

                            values = (repeat_idx_1, repeat_idx_2, hmm_state_id_1, hmm_state_id_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)

                            value = float(row[11])
                            sequence_type_id = squence_types_dict["PURINE"]
                            values = (repeat_idx_1, repeat_idx_2, hmm_state_id_1, hmm_state_id_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)

                            value = float(row[12])
                            sequence_type_id = squence_types_dict["AMINO"]
                            values = (repeat_idx_1, repeat_idx_2, hmm_state_id_1, hmm_state_id_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)

                            value = float(row[13])
                            sequence_type_id = squence_types_dict["WEAK_HYDROGEN"]
                            values = (repeat_idx_1, repeat_idx_2, hmm_state_id_1, hmm_state_id_2,
                                      value, metric_type_id, sequence_type_id, is_normalized)

                            batch_data.append(values)

                            if len(batch_data) >= batch_size:
                                database_wrap.execute_transaction(data=batch_data, sql=insert_sql)
                                batch_data = []

                        if len(batch_data) != 0:
                            database_wrap.execute_transaction(data=batch_data, sql=insert_sql)
                            batch_data = []
    print("{0} Done....".format(INFO))


def create_repeats_distances_table(database_wrap: SQLiteDBConnector,
                                   data_dir: Path, metrics: dir) -> None:

    """
    Populate the repeats_distances table
    """

    print("{0} Creating table repeats_distances...".format(INFO))
    if len(metrics) == 0:
        print("{0} Metrics map is empty exiting...".format(INFO))

    database_wrap.create_table(table_name="repeats_distances")

    for metric in metrics:
        directory_path = data_dir / metric

        if os.path.isdir(directory_path):

            short_cut = metric

            if short_cut in metrics:
                metric_data = database_wrap.fetch_from_distance_metric_type_table_by_short_cut(short_cut=short_cut)

                insert_distance_metric_result(database_wrap=database_wrap,
                                              metric_data=metric_data,
                                              directory_path=directory_path)

    print("{0} Done...".format(INFO))


def main(database_wrap: SQLiteDBConnector,
         repeats_file: Path,
         data_dir: Path,
         chromosomes_dir: Path,
         metrics: dir) -> None:

    tbl_names = ['repeats_distances', ]
    database_wrap.delete_all_tables(tbl_names=None)

    create_hmm_types_table(database_wrap=database_wrap)
    create_distance_types_table(database_wrap=database_wrap)
    create_distance_metrics_table(database_wrap=database_wrap, metrics=metrics)
    create_repeats_table(database_wrap=database_wrap, repeats_file=repeats_file)
    create_repeats_distances_table(database_wrap=database_wrap,
                                   data_dir=data_dir, metrics=metrics)


if __name__ == '__main__':

    db_file = "/home/alex/qi3/hmmtuf/play_ground.sqlite3"
    repeats_file = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/nucl_out.csv")
    data_dir = Path("/home/alex/qi3/hmmtuf/computations/distances/")
    chromosomes_dir = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/")


    metrics = {'ham': "Hamming", 'mlipns': "MLIPNS",
               'lev': "Levenshtein",
               'damlev': "DamerauLevenshtein",
               'jwink': "JaroWinkler",
               'str': "StrCmp95",
               'nw': "NeedlemanWunsch",
               'sw': "SmithWaterman",
               'got': "Gotoh",
               'jac': "Jaccard",
               'sor': "Sorensen",
               'tve': "Tversky", 'ov': "Overlap",
               'tan': "Tanimoto", 'cos': "Cosine",
               'mon': "MongeElkan",
               'bag': "Bag",
               'lcsseq': "LCSSeq",
               'lcsstr': "LCSStr", 'rat': "RatcliffObershelp",
               'ari': "ArithNCD", 'rle': "RLENCD",
               'bwt': "BWTRLENCD", 'sqr': "SqrtNCD",
               'ent': "EntropyNCD", 'bz2': "BZ2NCD", 'lzm': "LZMANCD",
               'zli': "ZLIBNCD", 'mra': "MRA", 'edi': "Editex",
               'pre': "Prefix", 'pos': "Postfix",
               'len': "Length", 'id': "Identity", 'mat': "Matrix",
              }

    metrics = { "bag": "Bag", "cos": "Cosine", 'damlev': "DamerauLevenshtein", 'got': "Gotoh",
    'ham': "Hamming", 'jac': "Jaccard", 'jwink': "JaroWinkler",
        'lcsseq': "LCSSeq", 'lcsstr': "LCSStr",
        'lev': "Levenshtein", 'mlipns': "MLIPNS", 'mon': "MongeElkan", 'nw': "NeedlemanWunsch",
        'ov': "Overlap", 'sor': "Sorensen", 'str': "StrCmp95", 'sw': "SmithWaterman",
        'tan': "Tanimoto", 'tve': "Tversky", }

    database_wrap = SQLiteDBConnector(db_file=db_file)
    database_wrap.connect()
    main(database_wrap=database_wrap, repeats_file=repeats_file,
         chromosomes_dir=chromosomes_dir,
         data_dir=data_dir, metrics=metrics)



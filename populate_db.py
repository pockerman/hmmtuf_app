import sqlite3
from sqlite3 import Error

import mysql.connector

INFO = "INFO:"
hmm_state_types = []
repeats_distances = []

distance_metrics = {"bag": "Bag", "cos": "Cosine", 'damlev': "DamerauLevenshtein", 'got': "Gotoh",
                    'ham': "Hamming", 'jac': "Jaccard", 'jwink': "JaroWinkler",
                    'lcsseq': "LCSSeq", 'lcsstr': "LCSStr",
                    'lev': "Levenshtein", 'mlipns': "MLIPNS", 'mon': "MongeElkan", 'nw': "NeedlemanWunsch",
                    'ov': "Overlap", 'sor': "Sorensen", 'str': "StrCmp95", 'sw': "SmithWaterman",
                    'tan': "Tanimoto", 'tve': "Tversky", }

def fillin_distance_types_table(db) -> None:

    print("{0} Creating table {1}...".format(INFO, "distance_sequence_type"))

    mycursor = db.cursor()

    CHOICES = [("NORMAL", "NORMAL"),
               ("PURINE", "PURINE"),
               ("AMINO", "AMINO"),
               ("WEAK_HYDROGEN", "WEAK_HYDROGEN"), ]

    for choice in CHOICES:
        sql = '''INSERT INTO distance_sequence_type(type) values(?)'''
        mycursor.execute(sql, (choice[0],))
        db.commit()
    print("{0} Done...".format(INFO))


def fillin_distance_metrics_table(db, distance_metrics: dir) -> None:

    print("{0} Creating table {1}...".format(INFO, "distance_metric_type"))
    mycursor = db.cursor()

    for met in distance_metrics:
        sql = '''INSERT INTO distance_metric_type(type, short_cut) values(?,?)'''
        mycursor.execute(sql, (distance_metrics[met], met))
        db.commit()

    print("{0} Done...".format(INFO))


def create_hmm_types_table(db) -> None:

    print("{0} Creating table {1}...".format(INFO, "hmm_state_types"))

    choices = ['NORMAL', 'TUF', 'DELETION', 'DUPLICATION']
    mycursor = db.cursor()

    for choice in choices:
        sql = '''INSERT INTO hmm_state_types(type) values(?)'''
        mycursor.execute(sql=sql, values=(choice,))
        db.commit()
    print("{0} Done...".format(INFO))


def populate_mysql(db):
    fillin_distance_types_table(db=db)
    fillin_distance_metrics_table(db=db, distance_metrics=distance_metrics)
    create_hmm_types_table(db=db)


if __name__ == '__main__':
    db_type = 'mysql'

    if db_type == 'sqlite3':
        pass
    elif db_type == 'mysql':

        # connect to the DB
        mydb = mysql.connector.connect(host="127.0.0.1",
                                       user="lampuser",
                                       password="changeme",
                                       database="hmmtuf_db_v1")

        populate_mysql(db=mydb)


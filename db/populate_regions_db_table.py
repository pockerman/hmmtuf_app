import sqlite3
from sqlite3 import Error
import csv
from shutil import copyfile


def connect(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(str(e))
    return conn


def fillin_group_tip_tbl(db_filename, db_input_filename):

    with open(db_input_filename, 'r', newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        group_tips = []
        chromosomes = []
        row_counter = 0
        for line in reader:

            if row_counter == 0:
                row_counter += 1
                continue

            group_tip = line[-1]
            chromosome = line[5]
            #chromosome_idx = line[6]

            if group_tip not in group_tips:
                group_tips.append(group_tip)
                chromosomes.append(chromosome)

        conn = connect(db_file=db_filename)
        cursor = conn.cursor()
        for tip, chromo in zip(group_tips, chromosomes):
            print("Add tip {0}, chromosome {1} pair in the DB".format(tip, chromo))
            sql = '''INSERT INTO region_group_tip(tip, chromosome) values(?,?)'''
            cursor.execute(sql, (tip, chromo))
            conn.commit()

def fill_in_region_tbl(db_filename, db_input_filename,
                       regions_store_path, regions_org_files_path, seq_data_path):

        with open(db_input_filename, 'r', newline='\n') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            conn = connect(db_file=db_filename)
            cur = conn.cursor()

            row_counter = 0
            for line in reader:

                if row_counter == 0:
                    row_counter += 1
                    continue

                group_tip = line[-1]

                # find the group tip
                cur.execute("SELECT * FROM region_group_tip WHERE tip=?", (group_tip,))
                row = cur.fetchone()
                tip_id = row[0]

                cur = conn.cursor()

                ref_seq_file = seq_data_path + line[2]
                wga_seq_file = seq_data_path + line[3]
                no_wga_seq_file = seq_data_path + line[4]
                chromosome = line[5]
                chromosome_idx = int(line[6])
                start_idx = int(line[7])
                end_idx = int(line[8])
                region_file_name = line[0]

                region_file_name_items = region_file_name.split('_')
                region_name = 'region_'+region_file_name_items[3]+'_'+chromosome
                file_region = regions_store_path + region_name + '.txt'

                sql = '''INSERT INTO region_model (name, extension,  file_region, 
                                                    chromosome,  chromosome_index, 
                                                    ref_seq_file, wga_seq_file, no_wga_seq_file, 
                                                    start_idx, end_idx, group_tip_id ) values(?, ?, ?, ?, ?, ?, 
                                                    ?, ?, ?, ?, ?)'''

                cur.execute(sql, (region_name, 'txt', file_region,
                                  chromosome, chromosome_idx, ref_seq_file,
                                  wga_seq_file, no_wga_seq_file, start_idx, end_idx, tip_id))
                conn.commit()

                # cp the region file
                copyfile(src=regions_org_files_path + region_file_name, dst=regions_store_path + region_name + '.txt')


def main(db_filename, db_input_filename, regions_store_path,
         regions_org_files_path, seq_data_path):

    fillin_group_tip_tbl(db_filename=db_filename, db_input_filename=db_input_filename)
    fill_in_region_tbl(db_filename=db_filename,
                       db_input_filename=db_input_filename,
                       regions_store_path=regions_store_path,
                       regions_org_files_path=regions_org_files_path,
                       seq_data_path=seq_data_path)


if __name__ == '__main__':
    db_filename = '../db.sqlite3'
    db_input_filename = '/regions_descriptions.csv'
    regions_store_path = '/regions/'
    regions_org_files_path = '/home/alex/qi3/hidden_markov_modeling/data/'
    seq_data_path = '/data/'
    main(db_filename=db_filename,
         db_input_filename=db_input_filename,
         regions_store_path=regions_store_path,
         regions_org_files_path=regions_org_files_path,
         seq_data_path=seq_data_path)
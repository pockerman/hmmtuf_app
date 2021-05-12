import sqlite3
from sqlite3 import Error
import csv
from shutil import copyfile
from pathlib import Path


def connect(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(str(e))
    return conn


def fillin_group_tip_tbl(db_filename: Path, db_input_filename: Path):

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
            chromosome = line[0]

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


def fill_in_region_tbl(db_filename: Path, db_input_filename: Path,
                       regions_store_path: Path,
                       regions_org_files_path: Path, seq_data_path: Path) -> None:

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

                #cur = conn.cursor()

                chromosome = line[0]
                ref_seq_file = seq_data_path / line[3]
                wga_seq_file = seq_data_path / line[4]
                no_wga_seq_file = seq_data_path / line[5]

                chromosome_idx = int(line[6])
                start_idx = int(line[7])
                end_idx = int(line[8])
                region_file_name = line[2]

                region_file_name_items = region_file_name.split('_')
                region_name = 'region_' + region_file_name_items[3] + '_'+chromosome
                region_name_extension = region_name + '.txt'
                file_region = regions_store_path / region_name_extension

                sql = '''INSERT INTO region_model (name, extension,  file_region, 
                                                    chromosome,  chromosome_index, 
                                                    ref_seq_file, wga_seq_file, no_wga_seq_file, 
                                                    start_idx, end_idx, group_tip_id ) values(?, ?, ?, ?, ?, ?, 
                                                    ?, ?, ?, ?, ?)'''

                cur.execute(sql, (region_name, 'txt', str(file_region),
                                  chromosome, chromosome_idx, str(ref_seq_file),
                                  str(wga_seq_file), str(no_wga_seq_file), start_idx, end_idx, tip_id))
                conn.commit()

                # cp the region file
                copyfile(src=regions_org_files_path / chromosome / region_file_name, dst=regions_store_path / region_name)


def main(db_filename: Path, db_input_filename: Path,
         regions_store_path: Path,
         regions_org_files_path: Path, seq_data_path: Path) -> None:

    fillin_group_tip_tbl(db_filename=db_filename, db_input_filename=db_input_filename)
    fill_in_region_tbl(db_filename=db_filename,
                       db_input_filename=db_input_filename,
                       regions_store_path=regions_store_path,
                       regions_org_files_path=regions_org_files_path,
                       seq_data_path=seq_data_path)


if __name__ == '__main__':

    db_filename = Path('../hmmtuf_db.sqlite3')
    db_input_filename = Path('/home/alex/qi3/hmmtuf/data/regions/regions_descriptions.csv')
    regions_store_path = Path('/home/alex/qi3/hmmtuf/regions/')
    regions_org_files_path = Path('/home/alex/qi3/hmmtuf/data/regions/')
    seq_data_path = Path('/home/alex/qi3/hmmtuf/data/')
    #main(db_filename=db_filename,
    #     db_input_filename=db_input_filename,
    #     regions_store_path=regions_store_path,
    #     regions_org_files_path=regions_org_files_path,
    #     seq_data_path=seq_data_path)

    sql = '''INSERT INTO region_model (name, extension, file_region, 
                                       chromosome,  chromosome_index, 
                                       ref_seq_file, wga_seq_file, no_wga_seq_file, 
                                       start_idx, end_idx, group_tip_id ) values(?, ?, ?, ?, ?, ?, 
                                                        ?, ?, ?, ?, ?)'''

    region_name = 'region_7_chr16'
    file_region = "/home/alex/qi3/hmmtuf/regions/region_7_chr16.txt"
    chromosome = 'chr16'
    start_idx = 30000000
    end_idx = 35000000
    chromosome_idx = 16
    tip_id = 7
    ref_seq_file = "/home/alex/qi3/hmmtuf/data/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna"
    wga_seq_file = "/home/alex/qi3/hmmtuf/data/m605_verysensitive_trim_sorted.bam"
    no_wga_seq_file = "/home/alex/qi3/hmmtuf/data/m585_verysensitive_trim_sorted.bam"

    conn = connect(db_file=db_filename)
    cur = conn.cursor()
    cur.execute(sql, (region_name, 'txt', str(file_region),
                      chromosome, chromosome_idx, str(ref_seq_file),
                      str(wga_seq_file), str(no_wga_seq_file), start_idx, end_idx, tip_id))
    conn.commit()
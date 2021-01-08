import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

from compute_engine.src.utils import read_bed_files, find_smallest_sequence, bisect_seqs
from compute_engine.src.constants import INFO


def compute_with_minimum_sequence(infile_dir, filenames, outfile_dir, outfilename, **options):

    with open(outfile_dir + outfilename, 'a', newline='\n') as out_fh:
        outfile_writer = csv.writer(out_fh, delimiter=',')

        if filenames is None:

            dir_list = os.listdir(infile_dir)
            seqs_total = dict()
            for directory in dir_list:

                if os.path.isdir(infile_dir + directory):

                    print("{0} processing directory {1}".format(INFO, directory))
                    filenames = os.listdir(infile_dir + directory)

                    for i in range(len(filenames)):
                        filenames[i] = infile_dir + directory + '/' + filenames[i] + '/nucl_out.bed'

                    seqs = read_bed_files(file_dir=infile_dir, filenames=filenames, concatenate=False)
                    seqs_total.update(seqs)

            # compute minimum sequence
            min_size, min_seq = find_smallest_sequence(seqs=seqs_total)
            print("{0} Minimum size sequence {1} is {2}".format(INFO, min_seq, min_size))

            sequences = bisect_seqs(seqs=seqs_total, size=min_size)
            for s in sequences:
                row = [s]
                outfile_writer.writerow(row)
        else:

            seqs = read_bed_files(file_dir=infile_dir, filenames=filenames, concatenate=False)

            for s in seqs:
                row = [s, seqs[s]]
                outfile_writer.writerow(row)


def main(infile_dir, filenames, outfile_dir, outfilename, **options):

    if "compute_with_minimum_sequence" in options:
        compute_with_minimum_sequence(infile_dir=infile_dir,
                                      filenames=filenames, outfile_dir=outfile_dir,
                                      outfilename=outfilename, **options)
        return

    with open(outfile_dir + outfilename, 'a', newline='\n') as out_fh:
        outfile_writer = csv.writer(out_fh, delimiter=',')

        if filenames is None:

            dir_list = os.listdir(infile_dir)

            for directory in dir_list:

                if os.path.isdir(infile_dir + directory):

                    print("{0} processing directory {1}".format(INFO, directory))
                    filenames = os.listdir(infile_dir + directory)

                    for i in range(len(filenames)):
                        filenames[i] = infile_dir + directory + '/' + filenames[i] + '/nucl_out.bed'

                    seqs = read_bed_files(file_dir=infile_dir, filenames=filenames, concatenate=False)

                    for s in seqs:
                        row = [seqs[s]]
                        outfile_writer.writerow(row)
        else:

            seqs = read_bed_files(file_dir=infile_dir, filenames=filenames, concatenate=False)

            for s in seqs:
                row = [s, seqs[s]]
                outfile_writer.writerow(row)


if __name__ == '__main__':

    print("{0} Start combine bed files app...".format(INFO))

    OUTPUT_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/output/"
    OUTPUT_FILE = "full_sequences_all.csv"
    FILE_DIR = "/home/alex/qi3/hmmtuf/computations/sequence_clusters/data/"
    FILENAMES = None

    main(infile_dir=FILE_DIR, filenames=FILENAMES,
         outfile_dir=OUTPUT_DIR, outfilename=OUTPUT_FILE) #**{"compute_with_minimum_sequence": False})

    print("{0} Finished...".format(INFO))

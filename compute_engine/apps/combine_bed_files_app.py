import csv
import numpy as np
from pathlib import Path
import os

from compute_engine.src.constants import INFO
from compute_engine.src.file_readers import NuclOutFileReader, GQuadsFileReader, RepeatsInfoFileReader


def main(infile_dir: Path, input_filename: str,
         output_file_dir: Path, output_filename: str, **options):


    with open(output_file_dir / output_filename, 'w', newline="\n") as out_fh:

        outfile_writer = csv.writer(out_fh, delimiter=',')
        dir_list = os.listdir(infile_dir)

        found_repeats = dict()
        for directory in dir_list:

            directory_path = infile_dir / directory
            if os.path.isdir(directory_path):

                    print("{0} processing directory {1}".format(INFO, directory))
                    filename = directory_path / directory / input_filename
                    print(filename)

                    seq_reader = NuclOutFileReader(exclude_seqs=[])
                    seqs = seq_reader(filename=filename)

                    filename = directory_path / directory / 'gquads.txt'
                    gquads_reader = GQuadsFileReader()
                    gquads = gquads_reader(filename=filename)

                    filename = directory_path / directory / 'repeates_info_file.bed'
                    repeats_info_reader = RepeatsInfoFileReader()
                    repeats = repeats_info_reader(filename=filename)

                    for s in seqs:
                        chromosome = s[0]
                        start = s[1]
                        end = s[2]
                        key = (chromosome, start, end)

                        value = gquads[key]
                        s.extend(value)

                        # we have no repeats
                        if s[3] == 'NO_REPEATS':
                            values = [0, "NO_REPEATS", "NO_REPEATS"]
                            s.extend(values)
                        else:
                            # we have repeats
                            repeats_val = repeats[key]

                            if key not in found_repeats:
                                found_repeats[key] = 0
                            else:
                                found_repeats[key] += 1

                            values = repeats_val[found_repeats[key]]
                            s.extend(values)

                        outfile_writer.writerow(s)

if __name__ == '__main__':

    print("{0} Start combine bed files app...".format(INFO))

    INPUT_FILE_DIR = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/")
    INPUT_FILE_NAME = "nucl_out.bed"
    OUTPUT_FILE_DIR = Path("/home/alex/qi3/hmmtuf/computations/viterbi_paths/")
    OUTPUT_FILE_NAME = "nucl_out.csv"

    main(infile_dir=INPUT_FILE_DIR, input_filename=INPUT_FILE_NAME,
         output_file_dir=OUTPUT_FILE_DIR, output_filename=OUTPUT_FILE_NAME)

    print("{0} Finished...".format(INFO))

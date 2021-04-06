"""
Utility functions for reading various
.bed files generated from SPADE processing
"""

import csv

def read_line_nucl_out_file(line: str, delimiter='\t') -> tuple:
    line_data = line.split(delimiter)
    chromosome = line_data[0]
    start = int(line_data[1])
    end = int(line_data[2])
    seq = str(line_data[3])
    state = str(line_data[4].rstrip("\n"))
    return chromosome, start, end, seq, state

def read_sequence_from_nucl_out_file(filename: str, exclude_seqs: list, delimiter: str='\t') -> list:

    with open(filename, 'r', newline="\n") as fh:
        seqs = []

        for line in fh:
            chromosome, start, end, seq, state = read_line_nucl_out_file(line=line, delimiter=delimiter)

            if seq not in exclude_seqs:
                seqs.append(seq)

        return seqs

def read_nucl_out_file(filename: str, exclude_seqs: list=["NO_REPEATS"], delimiter: str='\t'):

    with open(filename, 'r', newline="\n") as fh:
        seqs = []

        for line in fh:
            chromosome, start, end, seq, state = read_line_nucl_out_file(line=line, delimiter=delimiter)

            if seq not in exclude_seqs:
                seqs.append([chromosome, start, end, seq, state])

        return seqs


class CsvFileReader(object):

    def __init__(self, delimiter: str=',') -> None:
        self._delimiter = delimiter


    def __call__(self, filename) -> list:
        with open(filename, 'r', newline="\n") as fh:
            reader = csv.reader(fh, delimiter=self._delimiter)

            lines = []

            for line in reader:
                lines.append(line)
            return lines

class NuclOutFileReader(object):

    def __init__(self, exclude_seqs=["NO_REPEATS"], delimiter: str='\t') -> None:
        self._delimiter = delimiter
        self._exclude_seqs = exclude_seqs

    def __call__(self, filename) -> list:
        return read_nucl_out_file(filename=filename,
                                  exclude_seqs=self._exclude_seqs,
                                  delimiter=self._delimiter)

class NuclOutSeqFileReader(object):

    def __init__(self, exclude_seqs: list, delimiter: str='\t') -> None:
        self._delimiter = delimiter
        self._exclude_seqs = exclude_seqs

    def __call__(self, filename) -> list:
        return read_sequence_from_nucl_out_file(filename=filename,
                                                exclude_seqs=self._exclude_seqs,
                                                delimiter=self._delimiter)

class GQuadsFileReader(object):

    def __init__(self) -> None:
        pass

    def __call__(self, filename) -> dict:
        with open(filename, 'r', newline='\n') as fh:

            data_dir = dict()
            for line in fh:
                data = line.split(":")
                region = data[1].split("\t")
                has_repeats = False
                if 'True' in region[1]:
                    has_repeats = True

                region_data = region[0].split('_')
                start_end = region_data[0].split('-')

                chromosome = str(data[0])
                start = int(start_end[0])
                end = int(start_end[1])

                gc_avg = float(region_data[2])
                gc_min = region_data[3]
                gc_max = region_data[4]

                if gc_min == 'NA':
                    gc_min = -999.0
                else:
                    gc_min = float(gc_min)


                if gc_max == 'NA':
                    gc_max = -999.0
                else:
                    gc_max = float(gc_max)

                if (chromosome, start, end) in data_dir:
                    values = data_dir[(chromosome, start, end)]
                    if values[0] != gc_avg or values[1] != gc_min or values[2] != gc_max:
                        raise ValueError("key {0} already exists but values not equal")
                    else:
                        continue
                else:
                    data_dir[(chromosome, start, end)] = [gc_avg, gc_min, gc_max, has_repeats]

            return data_dir

class RepeatsInfoFileReader(object):

    def __init__(self) -> None:
        pass

    def __call__(self, filename) -> dict:
        with open(filename, 'r', newline='\n') as fh:

            data_dir = []
            for line in fh:
                data = line.split("\t")

                chromosome = str(data[0])
                start = int(data[1])
                end = int(data[2])
                n_repeats = int(data[3])
                seq1 = str(data[4].strip())
                seq2 = str(data[5].strip())
                data_dir.append([chromosome, start, end, n_repeats, seq1, seq2])

            return data_dir






"""
Utility functions for reading various
.bed files generated from SPADE processing
"""

def read_line_nucl_out_file(line: str, delimiter='\t') -> tuple:
    line_data = line.split(delimiter)
    chromosome = line_data[0]
    start = int(line_data[1])
    end = int(line_data[2])
    seq = line_data[3]
    state = line_data[4]
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


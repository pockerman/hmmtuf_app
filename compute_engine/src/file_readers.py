"""
Utility functions for reading various
.bed files generated from SPADE processing
"""

import csv
import json
from pathlib import Path

from compute_engine.src.enumeration_types import FileReaderType

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
"""
def read_nucl_out_file(filename: str, exclude_seqs: list=["NO_REPEATS"], delimiter: str='\t'):

    with open(filename, 'r', newline="\n") as fh:
        seqs = []

        for line in fh:
            chromosome, start, end, seq, state = read_line_nucl_out_file(line=line, delimiter=delimiter)

            if seq not in exclude_seqs:
                seqs.append([chromosome, start, end, seq, state])

        return seqs
"""


class CsvFileReader(object):

    def __init__(self, delimiter: str=',') -> None:
        self._delimiter = delimiter


    def __call__(self, filename: Path) -> list:
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

    def __call__(self, filename: Path) -> list:
        with open(filename, 'r', newline="\n") as fh:
            lines = []

            for line in fh:
                lines.append(line)
            return lines


class NuclOutSeqFileReader(object):

    def __init__(self, exclude_seqs: list, delimiter: str='\t') -> None:
        self._delimiter = delimiter
        self._exclude_seqs = exclude_seqs

    def __call__(self, filename: Path) -> list:
        return read_sequence_from_nucl_out_file(filename=filename,
                                                exclude_seqs=self._exclude_seqs,
                                                delimiter=self._delimiter)

class GQuadsFileReader(object):

    def __init__(self) -> None:
        pass

    def __call__(self, filename: Path) -> list:
        with open(filename, 'r', newline='\n') as fh:

            lines = []
            for line in fh:
                lines.append(line)
            return lines

    def read_as_dict(filename: Path) -> dict:
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

    def __call__(self, filename: Path) -> list:
        with open(filename, 'r', newline='\n') as fh:
            lines = []
            for line in fh:
                lines.append(line)
        return lines

    def get_as_fict(self, filename: Path) -> dict:
        with open(filename, 'r', newline='\n') as fh:

            data_dir = dict()
            for line in fh:
                data = line.split("\t")

                chromosome = str(data[0])
                start = int(data[1])
                end = int(data[2])

                key = (chromosome, start, end)
                n_repeats = int(data[3])
                seq1 = str(data[4].strip())
                seq2 = str(data[5].strip())

                if key in data_dir:
                    data_dir[key].append([n_repeats, seq1, seq2])
                else:
                    data_dir[key] = [[n_repeats, seq1, seq2]]

            return data_dir
            
            
class TufFileReader(object):

	def __init__(self) -> None:
		pass
		
	def __call__(self, filename: Path) -> list:
		
		with open(filename, 'r', newline='\n') as fh:
			lines = []
			for line in fh:
				lines.append(line)
		return lines


class DeletionFileReader(TufFileReader):
    def __init__(self) -> None:
        super(DeletionFileReader, self).__init__()


class DuplicationFileReader(TufFileReader):
    def __init__(self) -> None:
        super(DuplicationFileReader, self).__init__()


class GapFileReader(TufFileReader):
    def __init__(self) -> None:
        super(GapFileReader, self).__init__()


class NormalFileReader(TufFileReader):
    def __init__(self) -> None:
        super(NormalFileReader, self).__init__()


class TdtFileReader(TufFileReader):
    def __init__(self) -> None:
        super(TdtFileReader, self).__init__()


class QuadFileReader(TufFileReader):
    def __init__(self) -> None:
        super(QuadFileReader, self).__init__()


class RepFileReader(TufFileReader):
    def __init__(self) -> None:
        super(RepFileReader, self).__init__()


class ViterbiBedGraphReader(TufFileReader):
    def __init__(self) -> None:
        super(ViterbiBedGraphReader, self).__init__()


class JsonReader(object):
    def __init__(self) -> None:
        pass

    def __call__(self, filename: Path) -> dict:
        """
        Read the json configuration file and
        return a map with the config entries
        """
        with open(filename) as json_file:
            json_input = json.load(json_file)
            return json_input


class FileReaderFactory(object):
    def __init__(self, reader_type: FileReaderType) -> None:
        self._reader_type = reader_type

    def __call__(self, filename: Path, **kwargs):

        if self._reader_type == FileReaderType.TUF_BED:
            reader = TufFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.DELETION_BED:
            reader = DeletionFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.DUPLICATION_BED:
            reader = DuplicationFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.GAP_BED:
            reader = GapFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.NORMAL_BED:
            reader = NormalFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.TDT_BED:
            reader = TdtFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.VITERBI_BED_GRAPH:
            reader = ViterbiBedGraphReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.QUAD_BED:
            reader = QuadFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.REP_BED:
            reader = RepFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.REPEATS_INFO_BED:
            reader = RepeatsInfoFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.GQUADS:
            reader = GQuadsFileReader()
            return reader(filename=filename)
        elif self._reader_type == FileReaderType.NUCL_OUT:
            reader = NuclOutFileReader(exclude_seqs=kwargs["exclude_seqs"] if "exclude_seqs" in kwargs else [])
            return reader(filename=filename)
        else:
            raise ValueError("Unknown FileReaderType={0}".format(self._reader_type))






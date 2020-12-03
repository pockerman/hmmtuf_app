import numpy as np
import textdistance

from compute_engine.src.exceptions import Error
from compute_engine.src.utils import read_sequence_bed_file
from compute_engine.src.cpf import CPF


class L2Norm(object):
    """
    Simple wrapper for L2-norm calculation
    to adapt to text similarity
    """
    def __init__(self):
        pass

    def similarity(self, seq1, seq2):
        return np.linalg.norm(seq1 - seq2)


class TextDistanceCalculator(object):

    NAMES = ["Prefix similarity", "Postfix similarity",
             "Length distance", "Identity similarity",
             "Matrix similarity", "Longest common subsequence similarity",
             "Longest common substring similarity",
             "Ratcliff-Obershelp similarity", "L2Norm", 'CPF']

    @staticmethod
    def build_calculator(name):

        if name not in TextDistanceCalculator.NAMES:
            raise Error("Distance type '{0}' is invalid".format(name))

        if name == 'Prefix similarity':
            return textdistance.algorithms.simple.Prefix()
        elif name == "Postfix similarity":
            return textdistance.algorithms.simple.Postfix()
        elif name == "Length distance":
            return textdistance.algorithms.simple.Length()
        elif name == "Identity similarity":
            return textdistance.algorithms.simple.Identity()
        elif name == "Matrix similarity":
            return textdistance.algorithms.simple.Matrix()
        elif name == "Longest common subsequence similarity":
            return textdistance.algorithms.sequence_based.LCSSeq()
        elif name == "Longest common substring similarity":
            return textdistance.algorithms.sequence_based.LCSStr()
        elif name == "Ratcliff-Obershelp similarity":
            return textdistance.algorithms.sequence_based.RatcliffObershelp()
        elif name == "L2Norm":
            return L2Norm()
        elif name == 'CPF':
            return CPF()

    @staticmethod
    def read_sequence_comparison_file(filename, strip_path, delim=',', commment_delim='#'):

        with open(filename, 'r') as f:
            similarity_map = {}

            for line in f:

                if line.startswith(commment_delim):
                    continue

                line = line.split(delim)

                if strip_path:
                    line[0] = line[0].split('/')[-1]
                    line[1] = line[1].split('/')[-1]
                similarity_map[(line[0], line[1])] = float(line[2])

            return similarity_map

    def __init__(self, dist_type):

        if dist_type not in TextDistanceCalculator.NAMES:
            raise Error("Distance type '{0}' is invalid".format(dist_type))

        self._dist_type = dist_type

    def calculate(self, txt1, txt2):
        pass

    def calculate_from_files(self, fileslist, save_at, delim):

        sequences = []
        for file in fileslist:
            sequences.append(read_sequence_bed_file(filename=file[1], delim=delim))

        calculator = TextDistanceCalculator.build_calculator(name=self._dist_type)
        similarity_map = {}
        for seqi in range(len(sequences)):
            for seqj in range(len(sequences)):
                if seqi != seqj:
                    result = calculator.similarity(sequences[seqi], sequences[seqj])
                    similarity_map[(fileslist[seqi][0], fileslist[seqj][0])] = result

        if save_at is not None:
            with open(save_at, 'w') as f:
                f.write("#Sequence 1,Sequence 2,Similarity\n")

                for item in similarity_map:
                    f.write(item[0]+","+item[1]+","+str(similarity_map[(item[0], item[1])])+"\n")








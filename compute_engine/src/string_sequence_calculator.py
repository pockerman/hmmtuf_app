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


class AllDistancesCalculator(object):
    """
    Wrapper for calculating all the distances
    """
    def __init__(self):
        pass

    def similarity(self, seq1, seq2):

        results = {}

        results['ham'] = textdistance.Hamming().distance(seq1, seq2)
        results['mlipns'] = textdistance.MLIPNS().distance(seq1, seq2)
        results['lev'] = textdistance.Levenshtein().distance(seq1, seq2)
        results['damlev'] = textdistance.DamerauLevenshtein().distance(seq1, bseq2)
        results['jwink'] = textdistance.JaroWinkler().distance(seq1, seq2)
        results['str'] = textdistance.StrCmp95().distance(seq1, seq2)
        results['nw'] = textdistance.NeedlemanWunsch().distance(seq1, seq2)
        results['got'] = textdistance.Gotoh().distance(seq1, seq2)
        results['jac'] = textdistance.Jaccard().distance(seq1, seq2)
        results['sor'] = textdistance.Sorensen().distance(seq1, seq2)
        results['tve'] = textdistance.Tversky().distance(seq1, seq2)
        results['ov'] = textdistance.Overlap().distance(seq1, seq2)
        results['tan'] = textdistance.Tanimoto().distance(seq1, seq2)
        results['cos'] = textdistance.Cosine().distance(seq1, seq2)
        results['mon'] = textdistance.MongeElkan().distance(seq1, seq2)
        results['bag'] = textdistance.Bag().distance(seq1, seq2)
        results['lcsseq'] = textdistance.LCSSeq().distance(seq1, seq2)
        results['lcsstr'] = textdistance.LCSStr().distance(seq1, seq2)
        results['rat'] = textdistance.RatcliffObershelp().distance(seq1, seq2)
        results['ari'] = textdistance.ArithNCD().distance(seq1, seq2)
        results['rle'] = textdistance.RLENCD().distance(seq1, seq2)
        results['bwt'] = textdistance.BWTRLENCD().distance(seq1, seq2)
        results['sqr'] = textdistance.SqrtNCD().distance(seq1, seq2)
        results['ent'] = textdistance.EntropyNCD().distance(seq1, seq2)
        results['bz2'] = textdistance.BZ2NCD().distance(seq1, seq2)
        results['lzm'] = textdistance.LZMANCD().distance(seq1, seq2)
        results['zli'] = textdistance.ZLIBNCD().distance(seq1, seq2)
        results['mra'] = textdistance.MRA().distance(seq1, seq2)
        results['edi'] = textdistance.Editex().distance(seq1, seq2)
        results['pre'] = textdistance.Prefix().distance(seq1, seq2)
        results['pos'] = textdistance.Postfix().distance(seq1, seq2)
        results['len'] = textdistance.Length().distance(seq1, seq2)
        results['id'] = textdistance.Identity().distance(seq1, seq2)
        results['mat'] = textdistance.Matrix().distance(seq1, seq2)

        return results


class TextDistanceCalculator(object):
    """
    Wrapper class for text distance calculation
    """

    NAMES = ['ham', 'mlipns', 'lev', 'damlev', 'jwink', 'str'
            , 'nw', 'got', 'jac', 'sor', 'tve', 'ov', 'tan', 'cos', 'mon'
            , 'bag', 'lcsseq', 'lcsstr', 'rat', 'ari', 'rle', 'bwt', 'sqr'
            , 'ent', 'bz2', 'lzm', 'zli', 'mra', 'edi', 'pre', 'pos', 'len', 'id', 'mat'
            , 'size', 'mins', 'maxs', 'diff', 'seqpair', 'CPF', 'all']

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

    def calculate(self, txt1, txt2, **options):

        # build a calculator
        calculator = TextDistanceCalculator.build_calculator(name=self._dist_type)

        set_options = getattr(calculator, "set_options", None)

        if set_options is not None:
            calculator.set_options(**options)

        return calculator.similarity(txt1, txt2)

    def calculate_from_file(self, filename, file_reader, **options):
        """
        Calculate the similarity of the sequences in the
        filename. The file is read using the file_reader object.
        The file_reader should override the __call__ method
        that returns a list of strings. It returns a map where
        the key is (seq1, seq2) tuple and the value the
        similarity calculated
        """

        if file_reader is None:
            raise ValueError("file_reader not specified")

        # read the file
        sequences = file_reader(filename)

        # build a calculator
        calculator = TextDistanceCalculator.build_calculator(name=self._dist_type)

        # do we have set_options function?
        set_options = getattr(calculator, "set_options", None)

        if set_options is not None:
            calculator.set_options(**options)

        similarity_map = {}
        for seqi in range(len(sequences)):
            for seqj in range(len(sequences)):
                if seqi != seqj:
                    result = calculator.similarity(sequences[seqi], sequences[seqj])
                    similarity_map[(sequences[seqi], sequences[seqj])] = result

        return similarity_map

    def calculate_from_files(self, fileslist, save_at, delim, **options):

        sequences = []
        for file in fileslist:
            sequences.append(read_sequence_bed_file(filename=file[1], delim=delim))

        calculator = TextDistanceCalculator.build_calculator(name=self._dist_type)

        # do we have set_options function?
        set_options = getattr(calculator, "set_options", None)

        if set_options is not None:
            calculator.set_options(**options)

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








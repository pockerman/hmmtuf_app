import numpy as np
import math
import itertools
from itertools import islice

# categories according to paper
categories = {'C1': {"R": ['A', 'G'], "Y": ["C", "T"]},
              'C2': {"M": ['A', 'C'], "K": ["G", "T"]},
              'C3': {"W": ['A', 'T'], "S": ["C", "G"]}}

# possible words for every category
categories_words = {'C1': ['RR', 'RY', 'YR', 'YY'],
                    'C2': ['MM', 'MK', 'KM', 'KK'],
                    'C3': ['WW', 'WS', 'SW', 'SS']}

# complements
complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}


def reverse_complement(seq):
    t = ''
    for base in seq:
        t = complement[base] + t
    return t


def map_seq_to_category(category, seq):
    """
    project the original seq into
    the given category
    """

    new_seq = ''
    g1 = category[list(category.keys())[0]]
    g2 = category[list(category.keys())[1]]

    for base in seq:

        if base in g1:
            new_seq += list(category.keys())[0]
        elif base in g2:
            new_seq += list(category.keys())[1]
        else:
            raise ValueError("base {0} not in {1} or in {2}".format(base, g1, g2))
    return new_seq


def get_sliding_window_sequence_words(seq, w):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, w))
    if len(result) == w:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def collect_words(seq, k):
    words = []

    for word in get_sliding_window_sequence_words(seq=seq, w=k):
        words.append(word)
    return words


def shannon_entropy(ps):
    """
    Shannon entropy computation
    """

    entropy = 0.0

    for val in ps:

        if val < 1.0e-4:
            continue

        entropy += -val * math.log(val, 2)

    return entropy


def local_frequency(word, seq):
    """
    Compute the local frequency of the word
    in the qiven sequence
    """

    # this the counter which tracks
    # the occurences of the word in the
    # seq. 
    r = 1

    # indexes will hold the locations of the 
    # word in the sequence. so len(indexes)
    # indicates how many times the word is found in the
    # sequence
    indexes = []
    for item in seq:

        if item == word:
            indexes.append(r)

        r += 1

    if len(indexes) == 0:
        print("WARNING: Word {0} not found in the sequence {1}".format(word, seq))
        return [0]

    if len(indexes) == 1:
        return [1.0 / indexes[0]]

    frequencies = []

    for i in range(len(indexes)):

        current = indexes[i]
        if i != 0:

            previous = indexes[i - 1]
            frequencies.append(1.0 / (current - previous))
        else:

            frequencies.append(1.0 / current)

    return frequencies


def partial_sums(seq):
    """
    Compute the partial sums of the sequence
    """

    return list(itertools.accumulate(seq))


def sequence_total_sum(s):
    return sum(s)


def calculate_p(s, z):
    probabilities = []

    for item in s:
        probabilities.append(item / z)

    return probabilities


def sequence_feature_vector(seq, k=2):
    """
    Build the feature vector for the given sequence using
    a word size k=2
    """

    # placeholder for shannon entropies
    feature_vec = []

    for C in categories:

        # print("Working with category: ", C)

        # map the bases in seq into the groups
        # of the category
        new_seq = map_seq_to_category(categories[C], seq)
        # print("New sequence is: ", new_seq)

        # collect the words in the sequence for
        # a sliding window of length k
        words = collect_words(seq=new_seq, k=k)

        # loop over the unique words that
        # each category can produce
        for word in categories_words[C]:

            tuple_word = (word[0], word[1])

            if tuple_word not in words:
                feature_vec.append(0.0)
                continue

            # print(word)

            # compute the local frequency sequence
            lf_w = local_frequency(word=tuple_word, seq=words)

            # compute the partial sums of the sequence 
            # which is basically the prefix sum
            S = partial_sums(seq=lf_w)

            # compute the total sum of the sequence with the
            # prefix sums
            z = sequence_total_sum(s=S)

            # calculate the sequence of probabilities
            probabilities = calculate_p(s=S, z=z)

            # compute the entropy
            entropy = shannon_entropy(ps=probabilities)

            # ...append it to list
            feature_vec.append(entropy)

    if len(feature_vec) != 12:
        raise ValueError("Invalid dimension for feature vector. {0} should be {1}".format(len(feature_vec), 12))

    return feature_vec


def cpf(seq1, seq2, k=2):
    feature_vec_1 = sequence_feature_vector(seq=seq1, k=k)
    feature_vec_2 = sequence_feature_vector(seq=seq2, k=k)

    # calculate Euclidean distance
    feature_vec_1 = np.array(feature_vec_1)
    feature_vec_2 = np.array(feature_vec_2)
    dist = np.linalg.norm(feature_vec_1 - feature_vec_2)

    return dist


class CPF(object):
    def __init__(self):
        pass

    def similarity(self, seq1, seq2):
        return cpf(seq1=seq1, seq2=seq2)

    def __call__(self, *args, **kwargs):
        return self.similarity(seq1=args[0], seq2=args[1])


def get_unique_words(seq):
    unique_words = []

    for item in seq:
        if item not in unique_words:
            unique_words.append(item)

    return unique_words


def main():
    seq = 'ATGGTGCACCTGACT'
    dist = cpf(seq1=seq, seq2=seq)
    print("Seq1 {0}, seq2 {1} distance={2}".format(seq, seq, dist))

    reverse_complement_seq = reverse_complement(seq)
    dist = cpf(seq1=seq, seq2=reverse_complement_seq)
    print("Seq1 {0}, seq2 {1} distance={2}".format(seq, reverse_complement_seq, dist))

    reverse_complement_seq = reverse_complement_seq[0:5]
    dist = cpf(seq1=seq, seq2=reverse_complement_seq)
    print("Seq1 {0}, seq2 {1} distance={2}".format(seq, reverse_complement_seq, dist))


if __name__ == '__main__':
    main()

import json
from functools import wraps
import time
import os
from pathlib import Path

from compute_engine.src.constants import INFO, WARNING
from compute_engine.src.exceptions import Error

def timefn(fn):
    @wraps(fn)
    def measure(*args, **kwargs):
        time_start = time.perf_counter()
        result = fn(*args, **kwargs)
        time_end = time.perf_counter()
        print("{0} Done. Execution time"
              " {1} secs".format(INFO, time_end - time_start))
        return result

    return measure


def min_size_partition_range(start, end, minsize):

    if end <= start:
        raise Error("Range end cannot be smaller than start: {0} < {1}".format(end, start))

    if end - start <= minsize:
        return [(start, end)]

    chunks = []
    npieces = (end - start) // minsize

    start_c = start
    end_p = start_c + minsize
    for p in range(npieces - 1):
        chunks.append((start_c, end_p))
        start_c = end_p
        end_p += minsize

    chunks.append((start_c, end))
    return chunks

def partition_range(start, end, npieces):

    if npieces == 0:
        raise Error("Zero number of partitions")

    load = (end - start) // npieces

    chunks = []
    start_p = start

    end_p = start_p + load
    for p in range(npieces - 1):
        chunks.append((start_p, end_p))
        start_p = end_p
        end_p += load

    chunks.append((start_p, end))
    return chunks


def read_json(filename):

    """
        Read the json configuration file and
        return a map with the config entries
    """
    with open(filename) as json_file:
        json_input = json.load(json_file)
        return json_input


def read_bed_file(filename, concatenate):

    with open(filename, 'r') as fh:

        if concatenate:
            raise ValueError("Concatenation not implemented")
        else:
            seqs = dict()
            for line in fh:
                line_data = line.split('\t')
                chr = line_data[0]
                start = int(line_data[1])
                end = int(line_data[2])
                seq = line_data[3]

                if chr in seqs.keys():
                    seqs[chr].append((start, end, seq))
                else:
                    seqs[chr] = [(start, end, seq)]

            return seqs


def read_bed_files(file_dir, filenames, concatenate):

    dir_folder = Path(file_dir)

    if len(filenames) == 0:
        # get all filenames in the path
        filenames = os.listdir(path=dir_folder)

    if len(filenames) == 0:
        raise ValueError("Empty bed files list")

    print("{0} Processing bed files in {1}".format(INFO, file_dir))
    print("{0} Number of bed files given {1}".format(INFO, len(filenames)))

    if not concatenate:

        seqs_dict = dict()

        for filename in filenames:

            print("Processing ", filename)
            seqs = read_bed_file(filename=dir_folder / filename, concatenate=concatenate)

            if len(seqs.keys()) == 0:
                print("{0} filename is empty".format(WARNING, filename))
                continue

            chr_key = list(seqs.keys())[0]
            seqs = seqs[chr_key]

            for seq in seqs:
                counter = 0
                save_name = filename + '_' + chr_key + '_' + str(seq[0]) + '_' + str(seq[1]) + '_' + str(counter)

                if save_name not in seqs_dict:
                    seqs_dict[save_name] = seq[2]
                else:
                    counter += 1
                    save_name = filename + '_' + chr_key + '_' + str(seq[0]) + '_' + str(seq[1]) + '_' + str(counter)
                    while save_name in seqs_dict:
                        print("WEIRD: ", filename, save_name)

                        counter += 1
                        save_name = filename + '_' + chr_key + '_' + \
                                    str(seq[0]) + '_' + \
                                    str(seq[1]) + '_' + str(counter)

                    seqs_dict[save_name] = seq[2]

        return seqs_dict
    else:
        raise ValueError("Concatenation not implemented")


def compute_textdistances(sequences, distance_type, build_from_factory, compute_self_distances):
    """
    Compute the
    """

    if build_from_factory:
        #calculator = build_calculator(distance_type=distance_type)
        raise ValueError("Building from factory not implemented")
    else:
        calculator = distance_type

    similarity_map = dict()
    if isinstance(sequences, dict):

        seq_names = sequences.keys()

        for i, name1 in enumerate(seq_names):
            for j, name2 in enumerate(seq_names):

                if compute_self_distances:

                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map:
                        result = calculator.similarity(sequences[name1], sequences[name2])
                        similarity_map[name1, name2] = result
                else:

                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map and i != j:
                        result = calculator.similarity(sequences[name1], sequences[name2])
                        similarity_map[name1, name2] = result

    else:

        for i, name1 in enumerate(sequences):
            for j, name2 in enumerate(sequences):

                if compute_self_distances:
                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map:
                        result = calculator.similarity(name1, name2)
                        similarity_map[name1, name2] = result
                else:

                    if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map and i != j:
                        result = calculator.similarity(name1, name2)
                        similarity_map[name1, name2] = result


    return similarity_map


def extract_file_names(configuration):

    reference_files_names = []
    wga_files_names = []
    nwga_files_names = []
    files = configuration["sequence_files"]["files"]

    for idx in range(len(files)):
        map = files[idx]
        ref_files = map["ref_files"]
        reference_files_names.extend(ref_files)

        wga_files = map["wga_files"]
        wga_files_names.extend(wga_files)

        nwga_files = map["no_wga_files"]
        nwga_files_names.extend(nwga_files)

    return reference_files_names, wga_files_names, nwga_files_names


def extract_path(configuration, ref_file):
    files = configuration["sequence_files"]["files"]

    for idx in range(len(files)):
        map = files[idx]
        ref_files = map["ref_files"]

        if ref_file in ref_files:
            return map["path"]
    return None


def get_sequence_name(configuration, seq):
    return configuration["sequences_names"][seq]


def get_tdf_file(configuration, seq):
    return configuration["tdf_files"][seq]


def read_sequence_bed_file(filename, delim='\t'):

    sequence = ''
    with open(filename, 'r') as f:
        for line in f:
            line = line.split(delim)
            sequence += line[-1].strip('\n')

    return sequence







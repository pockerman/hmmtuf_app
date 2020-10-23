import json
import argparse
import textdistance
import os
from pathlib import Path


EMPTY_SEQ = ''
INFO = "INFO:"
WARNING = "WARNING:"


def read_configuration_file(config_file):
    """
    Read the json configuration file and
    return a map with the config entries
    """
    with open(config_file) as json_file:
        configuration = json.load(json_file)
        return configuration


def build_calculator(distance_type):

    NAMES = ["Prefix similarity", "Postfix similarity",
             "Length distance", "Identity similarity",
             "Matrix similarity", "Longest common subsequence similarity",
             "Longest common substring similarity",
             "Ratcliff-Obershelp similarity"]

    if distance_type not in NAMES:
        raise ValueError("Distance type '{0}' is invalid".format(distance_type))

    if distance_type == 'Prefix similarity':
        return textdistance.algorithms.simple.Prefix()
    elif distance_type == "Postfix similarity":
        return textdistance.algorithms.simple.Postfix()
    elif distance_type == "Length distance":
        return textdistance.algorithms.simple.Length()
    elif distance_type == "Identity similarity":
        return textdistance.algorithms.simple.Identity()
    elif distance_type == "Matrix similarity":
        return textdistance.algorithms.simple.Matrix()
    elif distance_type == "Longest common subsequence similarity":
        return textdistance.algorithms.sequence_based.LCSSeq()
    elif distance_type == "Longest common substring similarity":
        return textdistance.algorithms.sequence_based.LCSStr()
    elif distance_type == "Ratcliff-Obershelp similarity":
        return textdistance.algorithms.sequence_based.RatcliffObershelp()


def compute_textdistances(seq_dict, distance_type):
    """
    Compute the
    """
    calculator = build_calculator(distance_type=distance_type)

    seq_names = seq_dict.keys()

    similarity_map = dict()
    for name1 in seq_names:
        for name2 in seq_names:

            if (name1, name2) not in similarity_map and (name2, name1) not in similarity_map:
                result = calculator.similarity(seq_dict[name1], seq_dict[name2])
                similarity_map[name1, name2] = result

    return similarity_map


def read_bed_file(filename, concatenate):

    with open(filename, 'r') as fh:

        seq = ''
        if concatenate:
            pass
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


def read_weblogo_file(filename):
    """
    Read the weblogo file and form the sequence
    string
    """

    with open(filename, 'r') as f:
        count = 0
        nucleods = ['A', 'C', 'G', 'T']
        seq = EMPTY_SEQ
        for line in f:
            count += 1

            # don't process the comment line
            if line.startswith('#'):
                continue

            # checkout from the line which has the maximum
            new_line = line.split('\t')

            if len(new_line) > 5:
                new_line = new_line[1:5]
                new_line = [int(item) for item in new_line]
                max_item = max(new_line)
                nucleod_idx = new_line.index(max_item)

                if nucleod_idx >= 4:
                    raise ValueError("Invalid index for nucleod. "
                                     "Index {0} not in [0,3]".format(nucleod_idx))

                nucleod = nucleods[nucleod_idx]
                seq += nucleod

        return seq


def read_weblogos(file_dir, filenames):
    """
    Read a list of weblogo files
    """

    dir_folder = Path(file_dir)

    if len(filenames) == 0:
        # get all filenames in the path
        filenames = os.listdir(path=dir_folder)

    if len(filenames) == 0:
        raise ValueError("Empty weblogo file list")

    print("{0} Processing weblogo files in {1}".format(INFO, file_dir))
    print("{0} Number of weblogo files given {1}".format(INFO, len(filenames)))
    seq_dict = dict()

    dir_folder = Path(file_dir)

    for filename in filenames:
        seq_dict[filename] = read_weblogo_file(filename=dir_folder / filename)

    return seq_dict


def save_distances(output_dir, output_file, dist_map, remove_existing):
    dir_folder = Path(output_dir)
    files = os.listdir(dir_folder)

    if output_file not in files:
        mode = 'w'
    elif output_file in files and not remove_existing:
        mode = 'a'
    else:
        mode = 'w'

    print("{0} Write output distances in {1}".format(INFO, dir_folder / output_file))

    with open(dir_folder / output_file, mode) as f:
        for item in dist_map:
            f.write(item[0] + ',' + item[1] + ',' + str(dist_map[item]) + '\n')


def main(configuration):

    if not configuration["weblogo_dir"] == "":

        seq_dict = read_weblogos(file_dir=configuration["weblogo_dir"],
                                filenames=configuration["weblogos_files"])
    elif not configuration["bedfile_dir"] == "":
        seq_dict = read_bed_files(file_dir=configuration["bedfile_dir"],
                                  filenames=configuration["bedfiles"],
                                  concatenate=configuration["concatenate_seqs"])
    else:
        raise ValueError("Neither weblogos nor bed files have been specified")

    # compute distances...
    distance_type = configuration["distance_type"]
    similarity_map = compute_textdistances(seq_dict=seq_dict, distance_type=distance_type)

    # write to output file
    save_distances(output_dir=configuration['output_dir'], output_file=configuration['output_file'],
                   dist_map=similarity_map, remove_existing=configuration['replace_existing'])


if __name__ == '__main__':

    description = "No description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--config', type=str, default='config_with_bed.json',
                        help="You must specify a json "
                             "formatted configuration file")

    print("{0} Read configuration file".format(INFO))
    args = parser.parse_args()
    configuration = read_configuration_file(args.config)
    print("{0} Done...".format(INFO))

    print("{0} Starting...".format(INFO))
    main(configuration=configuration)
    print("{0} Finished...".format(INFO))





from pathlib import Path
import csv
from compute_engine.src.file_readers import NuclOutFileReader, GQuadsFileReader, RepeatsInfoFileReader

def main(repeats_out_filename: Path, nucl_out_bed: Path,
         gquads_bed: Path, repeats_info_bed: Path) -> None:

    with open(repeats_out_filename, 'w', newline='\n') as wfh:
        writer = csv.writer(wfh, delimiter=",")

        nucl_reader = NuclOutFileReader(exclude_seqs=[])
        nucl_data = nucl_reader(filename=nucl_out_bed)

        gquads = GQuadsFileReader(read_as_dict=True)
        gquads_data = gquads(filename=gquads_bed)

        repeats_info = RepeatsInfoFileReader(read_as_dict=True)
        repeats_data = repeats_info(filename=repeats_info_bed)
        repeats_data_multiple = dict()
        for item in nucl_data:

            chromosome = str(item[0].strip())
            start_idx = int(item[1])
            end_idx = int(item[2])
            repeat = str(item[3].strip())
            state = str(item[4].strip()).upper()

            gc_state = gquads_data[(chromosome, start_idx, end_idx)]

            if repeat != 'NO_REPEATS':
                rdata = repeats_data[(chromosome, start_idx, end_idx)]

                if len(rdata) > 1:
                    # we have multiple repeats

                    if (chromosome, start_idx, end_idx) in repeats_data_multiple:
                        next_valid_counter = repeats_data_multiple[(chromosome, start_idx, end_idx)]
                        repeats_data_multiple[(chromosome, start_idx, end_idx)] += 1
                    else:
                        next_valid_counter = 0
                        repeats_data_multiple[(chromosome, start_idx, end_idx)] = 1

                    assert next_valid_counter < len(rdata), "Invalid data index"

                    n_repeats = rdata[next_valid_counter][0]
                    align_seq = rdata[next_valid_counter][1]
                    unit_seq = rdata[next_valid_counter][2]
                    has_repeats = 1
                else:

                    n_repeats = rdata[0][0]
                    align_seq = rdata[0][1]
                    unit_seq = rdata[0][2]
                    has_repeats = 1

            else:
                n_repeats = 0
                align_seq = 'NO_ALIGN'
                unit_seq = 'NO_UNIT'
                has_repeats = 0


            gc = float(gc_state[0])
            gc_min = float(gc_state[1])
            gc_max = float(gc_state[2])

            #if seq[8] == 'True':
            #    has_repeats = 1

            #n_repeats = int(seq[9])
            #align_seq = str(seq[10])
            #unit_seq = str(seq[11])

            row = [chromosome, start_idx, end_idx, repeat, state,
                   gc, gc_max, gc_min, has_repeats,
                   n_repeats, align_seq, unit_seq]
            writer.writerow(row)




if __name__ == '__main__':

    DATA_IN_PATH = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths/tmp/')
    DATA_OUT_PATH = Path('/home/alex/qi3/hmmtuf/computations/viterbi_paths/tmp/out/')

    repeats_out_filename = DATA_OUT_PATH / 'nucl_out.csv'
    nucl_out_bed = DATA_IN_PATH / 'nucl_out_out.bed'
    gquads_bed = DATA_IN_PATH / 'gquads_out.txt'
    repeats_info_bed = DATA_IN_PATH / 'repeates_info_file_out.bed'
    main(repeats_out_filename=repeats_out_filename,
         nucl_out_bed=nucl_out_bed, gquads_bed=gquads_bed, repeats_info_bed=repeats_info_bed)
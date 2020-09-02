"""
Celery tasks for various computations
"""
import os
from celery.decorators import task
from celery.utils.log import get_task_logger

from hmmtuf_home.utils import INFO, ERROR

from . import utils
from . import region
from . import helpers

logger = get_task_logger(__name__)


@task(name="compute_viterbi_path_task")
def compute_viterbi_path_task(hmm_name, chromosome,
                              window_type, viterbi_path_filename,
                              region_filename, hmm_filename,
                              sequence_size, n_sequences, path_img, viterbi_path_files_root):


    from .models import ComputationResultEnum, DEFAULT_ERROR_EXPLANATION, ComputationType

    task_id = compute_viterbi_path_task.request.id
    task_id = task_id.replace('-', '_')

    result = {"hmm_filename": hmm_filename,
              "region_filename": region_filename,
              "task_id": task_id,
              "result": ComputationResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": ComputationType.VITERBI.name,
              "chromosome": chromosome}

    logger.info("Computing Viterbi path")

    if window_type == helpers.WindowType.BOTH.name:
            result["window_type"] = 'BOTH'
    elif window_type == helpers.WindowType.WGA.name:
            result["window_type"] = 'WGA'
    elif window_type == helpers.WindowType.NO_WGA.name:
            result["window_type"] = 'NO_WGA'
    else:
        print("{0} Window type {1}".format(INFO, window_type))

        # build the hmm model from the file
    hmm_model = utils.build_hmm(hmm_file=hmm_filename)

    if hmm_model is None:
        result["result"] = ComputationResultEnum.FAILURE.name
        result["error_explanation"] = "Could not build HMM model"
        return result

    hmm_path_img = path_img + str(task_id)

    try:
        os.mkdir(hmm_path_img)
    except OSError:
        result["result"] = ComputationResultEnum.FAILURE.name
        result["error_explanation"] = "Could not create dir: {0}".format(hmm_path_img)
        return result
    else:
            print("{0} Successfully created the directory {1}".format(INFO, hmm_path_img))

    hmm_path_img = hmm_path_img + '/' + hmm_name + '.png'
    utils.save_hmm_image(hmm_model=hmm_model, path=hmm_path_img)

    result['hmm_path_img'] = hmm_path_img

    reg = region.Region.load(filename=region_filename)
    reg.get_mixed_windows()

    print("{0} Region windows: {1}".format(INFO, reg.get_n_mixed_windows()))

    result["n_mixed_windows"] = reg.get_n_mixed_windows()

    window_type = helpers.WindowType.from_string(window_type)

    n_seqs = n_sequences
    result["n_seqs"] = n_seqs

    seq_size = sequence_size
    result["seq_size"] = seq_size

    chromosome = chromosome
    result["chromosome"] = chromosome

    viterbi_path_filename = viterbi_path_files_root + "/" + task_id + "/" + viterbi_path_filename
    result["viterbi_path_filename"] = viterbi_path_filename

    print("{0} Window type: {1}".format(INFO, window_type))
    print("{0} Sequence size: {1}".format(INFO, seq_size))
    print("{0} Number of sequences: {1}".format(INFO, n_seqs))

    sequence = reg.get_region_as_rd_mean_sequences_with_windows(size=seq_size,
                                                                window_type=window_type,
                                                                n_seqs=n_seqs,
                                                                exclude_gaps=False)

    result["extracted_sequences"] = len(sequence)
    result["seq_size"] = len(sequence)

    viterbi_path, observations, \
    sequence_viterbi_state = utils.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                           chr=chromosome, filename=viterbi_path_filename)
    # extract the tuf + Deletion + tuf
    tuf_delete_tuf = utils.filter_viterbi_path(path=viterbi_path[1][1:],
                                               wstate='TUF',
                                               limit_state='Deletion', min_subsequence=1)

    segments = utils.get_start_end_segment(tuf_delete_tuf, sequence)

    # filename = "/home/alex/qi3/hidden_markov_modeling/stories/" + viterbi_paths
    # filename = filename + "tuf_delete_tuf_" + computation.region_name
    # utils.save_segments(segments=segments, chromosome=chromosome, filename=filename)

    wga_obs = []
    no_wga_obs = []
    no_gaps_obs = []

    for obs in observations:

        # do not account for gaps
        if obs != (-999.0, -999.0):
            wga_obs.append(obs[0])
            no_wga_obs.append(obs[1])
            no_gaps_obs.append((obs[1], obs[0]))

    hmm_states_to_labels = {"Duplication": 0, "Normal-I": 1, "Normal-II": 2,
                                "Deletion": 3, "Single-Deletion": 4, "TUF": 5, "TUFDUP": 6}

    label_plot_filename = path_img + str(task_id) + '/' + 'viterbi_scatter.csv'
    color_comp_assoc_hmm, hmm_states_to_labels, hmm_labels = \
        utils.plot_hmm_states_to_labels(hmm_states_to_labels=hmm_states_to_labels,
                                      observations=observations,
                                      sequence_viterbi_state=sequence_viterbi_state,
                                      no_wga_obs=no_wga_obs, wga_obs=wga_obs,
                                      title="Region: [1-10]x10^6",
                                      xlim=(0.0, 150.), ylim=(0.0, 150.0),
                                      show_plt=False, save_file=True, save_filename=label_plot_filename)

    result["viterbi_label_plot_filename"] = label_plot_filename
    result["result"] = ComputationResultEnum.SUCCESS.name

    return result


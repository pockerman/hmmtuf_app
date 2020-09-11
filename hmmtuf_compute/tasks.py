"""
Celery tasks for various computations
"""
import os
from celery.decorators import task
from celery.utils.log import get_task_logger

from compute_engine import INFO, DEFAULT_ERROR_EXPLANATION
from compute_engine.job import JobType, JobResultEnum
from compute_engine import hmm_loader
from compute_engine import viterbi_calculation_helpers
from compute_engine.windows import WindowType
from compute_engine.region import Region

from hmmtuf.settings import HMM_FILES_ROOT, VITERBI_PATHS_FILES_ROOT
from hmmtuf_home.models import RegionModel, HMMModel

logger = get_task_logger(__name__)


@task(name="compute_mutliple_viterbi_path_task")
def compute_mutliple_viterbi_path_task(hmm_name, chromosome,
                                       window_type, viterbi_path_filename,
                                       path, ref_seq_file=None, wga_seq_file=None, no_wag_seq_file=None):

    logger.info("Computing Multi Viterbi path")
    from .models import MultiViterbiComputation

    task_id = compute_mutliple_viterbi_path_task.request.id
    viterbi_path_filename = VITERBI_PATHS_FILES_ROOT + "/" + task_id.replace('-', '_') + "/" + viterbi_path_filename

    computation = MultiViterbiComputation()
    computation.task_id = task_id
    computation.computation_type = JobType.MULTI_VITERBI
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.file_viterbi_path = viterbi_path_filename
    computation.save()

    result = {"task_id": task_id,
              "result": JobResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": JobType.VITERBI.name,
              "chromosome": chromosome,
              "ref_seq_file": ref_seq_file,
              "wga_seq_file": wga_seq_file,
              "no_wag_seq_file": no_wag_seq_file}

    if window_type == WindowType.BOTH.name:
        result["window_type"] = 'BOTH'
    elif window_type == WindowType.WGA.name:
        result["window_type"] = 'WGA'
    elif window_type == WindowType.NO_WGA.name:
        result["window_type"] = 'NO_WGA'
    else:
        print("{0} Window type {1}".format(INFO, window_type))

    window_type = WindowType.from_string(window_type)
    db_hmm_model = HMMModel.objects.get(name=hmm_name)
    hmm_filename = db_hmm_model.file_hmm.name

    print("{0} hmm_filename {1}".format(INFO, hmm_filename))

    # build the hmm model from the file
    hmm_model = hmm_loader.build_hmm(hmm_file=hmm_filename)

    if hmm_model is None:
        computation.error_explanation = "Could not build HMM model"
        computation.result = JobResultEnum.FAILURE.name
        computation.save()

        result["result"] = JobResultEnum.FAILURE.name
        result["error_explanation"] = "Could not build HMM model"
        return result

    # change to underscore to create dir
    task_id = task_id.replace('-', '_')
    hmm_path_img = VITERBI_PATHS_FILES_ROOT + task_id

    try:
        os.mkdir(hmm_path_img)
    except OSError:

        computation.error_explanation = "Could not create dir: {0}".format(hmm_path_img)
        computation.result = JobResultEnum.FAILURE.name
        computation.save()

        result["result"] = JobResultEnum.FAILURE.name
        result["error_explanation"] = "Could not create dir: {0}".format(hmm_path_img)
        return result
    else:
        print("{0} Successfully created the directory {1}".format(INFO, hmm_path_img))

    hmm_path_img = hmm_path_img + '/' + hmm_name + '.png'
    hmm_loader.save_hmm_image(hmm_model=hmm_model, path=hmm_path_img)

    # load the regions
    file_ = path + ref_seq_file
    regions = RegionModel.objects.filter(ref_seq_file=file_,
                                         chromosome=chromosome)
    for region_model in regions:
        region_filename = region_model.file_region.name

        print("{0} Region file name {1}".format(INFO, region_filename))
        region = Region.load(filename=region_filename)
        region.get_mixed_windows()

        try:

            # extract the sequence
            sequence = region.get_region_as_rd_mean_sequences_with_windows(size=None,
                                                                           window_type=window_type,
                                                                           n_seqs=1,
                                                                           exclude_gaps=False)

            viterbi_path, observations, \
            sequence_viterbi_state = viterbi_calculation_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                                     chr=chromosome,
                                                                                     filename=viterbi_path_filename,
                                                                                     append_or_write='a')
        except Exception as e:

            computation.result = JobResultEnum.FAILURE.name
            computation.error_explanation = str(e)
            computation.save()
            return result

    computation.result = JobResultEnum.SUCCESS.name
    computation.save()
    return result


@task(name="compute_viterbi_path_task")
def compute_viterbi_path_task(hmm_name, chromosome,
                              window_type, viterbi_path_filename,
                              region_filename, hmm_filename,
                              sequence_size, n_sequences,
                              path_img, viterbi_path_files_root, ref_seq_file,
                              wga_seq_file, no_wag_seq_file):

    task_id = compute_viterbi_path_task.request.id
    task_id = task_id.replace('-', '_')

    result = {"hmm_filename": hmm_filename,
              "region_filename": region_filename,
              "task_id": task_id,
              "result": JobResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": JobType.VITERBI.name,
              "chromosome": chromosome,
              "ref_seq_file": ref_seq_file,
              "wga_seq_file": wga_seq_file,
              "no_wag_seq_file": no_wag_seq_file}

    logger.info("Computing Viterbi path")

    if window_type == WindowType.BOTH.name:
            result["window_type"] = 'BOTH'
    elif window_type == WindowType.WGA.name:
            result["window_type"] = 'WGA'
    elif window_type == WindowType.NO_WGA.name:
            result["window_type"] = 'NO_WGA'
    else:
        print("{0} Window type {1}".format(INFO, window_type))

    # build the hmm model from the file
    hmm_model = hmm_loader.build_hmm(hmm_file=hmm_filename)

    if hmm_model is None:
        result["result"] = JobResultEnum.FAILURE.name
        result["error_explanation"] = "Could not build HMM model"
        return result

    hmm_path_img = path_img + str(task_id)

    try:
        os.mkdir(hmm_path_img)
    except OSError:
        result["result"] = JobResultEnum.FAILURE.name
        result["error_explanation"] = "Could not create dir: {0}".format(hmm_path_img)
        return result
    else:
        print("{0} Successfully created the directory {1}".format(INFO, hmm_path_img))

    hmm_path_img = hmm_path_img + '/' + hmm_name + '.png'
    hmm_loader.save_hmm_image(hmm_model=hmm_model, path=hmm_path_img)

    result['hmm_path_img'] = hmm_path_img

    region = Region.load(filename=region_filename)
    region.get_mixed_windows()

    print("{0} Region windows: {1}".format(INFO, region.get_n_mixed_windows()))

    result["n_mixed_windows"] = region.get_n_mixed_windows()

    window_type = WindowType.from_string(window_type)

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

    sequence = region.get_region_as_rd_mean_sequences_with_windows(size=seq_size,
                                                                window_type=window_type,
                                                                n_seqs=n_seqs,
                                                                exclude_gaps=False)

    result["extracted_sequences"] = len(sequence)
    result["seq_size"] = len(sequence)

    viterbi_path, observations, \
    sequence_viterbi_state = viterbi_calculation_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                             chr=chromosome, filename=viterbi_path_filename)
    # extract the tuf + Deletion + tuf
    #tuf_delete_tuf = viterbi_calculation_helpers.filter_viterbi_path(path=viterbi_path[1][1:],
    #                                                                 wstate='TUF',
    #                                                                 limit_state='Deletion', min_subsequence=1)

    #segments = viterbi_calculation_helpers.get_start_end_segment(tuf_delete_tuf, sequence)

    # filename = "/home/alex/qi3/hidden_markov_modeling/stories/" + viterbi_paths
    # filename = filename + "tuf_delete_tuf_" + computation.region_name
    # utils.save_segments(segments=segments, chromosome=chromosome, filename=filename)

    wga_obs = []
    no_wga_obs = []
    no_gaps_obs = []

    number_of_gaps = 0
    for obs in observations:

        # do not account for gaps
        if obs != (-999.0, -999.0):
            wga_obs.append(obs[0])
            no_wga_obs.append(obs[1])
            no_gaps_obs.append((obs[1], obs[0]))
        else:
            number_of_gaps += 1

    """
    hmm_states_to_labels = {"Duplication": 0,
                            "Normal-I": 1,
                            "Normal-II": 2,
                            "Deletion": 3,
                            "Single-Deletion": 4,
                            "TUF": 5, "TUFDUP": 6}
    """

    #label_plot_filename = path_img + str(task_id) + '/' + 'viterbi_scatter.csv'
    #color_comp_assoc_hmm, hmm_states_to_labels, hmm_labels = \
    #    viterbi_calculation_helpers.plot_hmm_states_to_labels(hmm_states_to_labels=hmm_states_to_labels,
    #                                                          observations=observations,
    #                                                          sequence_viterbi_state=sequence_viterbi_state,
    #                                                          no_wga_obs=no_wga_obs, wga_obs=wga_obs,
    #                                                          title="Region: [1-10]x10^6",
    #                                                          xlim=(0.0, 150.), ylim=(0.0, 150.0),
    #                                                          show_plt=False, save_file=True, save_filename=label_plot_filename)

    result["viterbi_label_plot_filename"] = "NO PLOT CREATED" #label_plot_filename
    result["result"] = JobResultEnum.SUCCESS.name
    result["number_of_gaps"] = number_of_gaps

    return result


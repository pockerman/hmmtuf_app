"""
Celery tasks for various computations
"""
import os
from celery.decorators import task
from celery.utils.log import get_task_logger

from compute_engine import INFO, DEFAULT_ERROR_EXPLANATION
from compute_engine.job import JobType, JobResultEnum
from compute_engine import hmm_loader
from compute_engine import viterbi_calculation_helpers as viterbi_helpers
from compute_engine.windows import WindowType
from compute_engine.region import Region
from compute_engine import tufdel

from hmmtuf import INVALID_ITEM
from hmmtuf.settings import VITERBI_PATHS_FILES_ROOT
from hmmtuf.helpers import make_viterbi_path_filename, make_viterbi_path, make_tuf_del_tuf_path_filename
from hmmtuf_home.models import RegionModel, HMMModel

logger = get_task_logger(__name__)


@task(name="compute_mutliple_viterbi_path_task")
def compute_mutliple_viterbi_path_task(hmm_name, chromosome,
                                       window_type, viterbi_path_filename,
                                       group_tip,
                                       ref_seq_file, wga_seq_file, no_wga_seq_file):

    logger.info("Computing Multi Viterbi path")
    from .models import MultiViterbiComputation

    task_id = compute_mutliple_viterbi_path_task.request.id
    #viterbi_task_path = VITERBI_PATHS_FILES_ROOT + task_id.replace('-', '_') + "/"
    #viterbi_path_filename =  viterbi_task_path + viterbi_path_filename
    viterbi_path_filename = make_viterbi_path_filename(task_id=task_id)

    # load the regions
    regions = RegionModel.objects.filter(group_tip__tip=group_tip,
                                         chromosome=chromosome)

    result = {"task_id": task_id,
              "result": JobResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": JobType.MULTI_VITERBI.name,
              "chromosome": chromosome,
              "ref_seq_filename": ref_seq_file,
              "wga_seq_filename": wga_seq_file,
              "no_wga_seq_filename": no_wga_seq_file,
              "hmm_filename": hmm_name,
              "file_viterbi_path": viterbi_path_filename,
              "n_regions": len(regions),
              "window_type": 'BOTH',
              'hmm_path_img': INVALID_ITEM}

    # create a computation instance
    computation = MultiViterbiComputation()
    computation.task_id = task_id
    computation.computation_type = JobType.MULTI_VITERBI.name
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.file_viterbi_path = viterbi_path_filename
    computation.chromosome = chromosome
    computation.hmm_filename = hmm_name
    computation.n_regions = len(regions)
    computation.ref_seq_filename = ref_seq_file
    computation.wga_seq_filename = wga_seq_file
    computation.no_wag_seq_filename = no_wga_seq_file
    computation.save()

    window_type = WindowType.from_string(window_type)
    db_hmm_model = HMMModel.objects.get(name=hmm_name)
    hmm_filename = db_hmm_model.file_hmm.name

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
        print("{0} Successfully created the directory {1}".format(INFO, hmm_path_img))
    except OSError:

        computation.error_explanation = "Could not create dir: {0}".format(hmm_path_img)
        computation.result = JobResultEnum.FAILURE.name
        computation.save()

        result["result"] = JobResultEnum.FAILURE.name
        result["error_explanation"] = "Could not create dir: {0}".format(hmm_path_img)
        return result

    hmm_path_img = hmm_path_img + '/' + hmm_name + '.png'
    hmm_loader.save_hmm_image(hmm_model=hmm_model, path=hmm_path_img)
    computation.hmm_path_img = hmm_path_img
    result['hmm_path_img'] = hmm_path_img

    print("{0} Saved HMM path image {1}".format(INFO, computation.hmm_path_img))

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
            sequence_viterbi_state = viterbi_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                         chr=chromosome, filename=viterbi_path_filename,
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
                              window_type,
                              region_filename, hmm_filename,
                              sequence_size, n_sequences,
                              ref_seq_file, wga_seq_file, no_wag_seq_file):

    logger.info("Computing Viterbi path")
    from .models import ViterbiComputation

    task_id = compute_viterbi_path_task.request.id
    viterbi_path_filename = make_viterbi_path_filename(task_id=task_id)

    computation = ViterbiComputation()
    computation.task_id = task_id
    computation.computation_type = JobType.VITERBI.name
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.file_viterbi_path = viterbi_path_filename
    computation.chromosome = chromosome
    computation.hmm_filename = hmm_name
    computation.region_filename = region_filename
    computation.ref_seq_filename = ref_seq_file
    computation.wga_seq_filename = wga_seq_file
    computation.no_wag_seq_filename = no_wag_seq_file
    computation.window_type = window_type
    computation.number_of_gaps = 0
    computation.seq_size = 0
    computation.n_mixed_windows = 0
    computation.extracted_sequences = 1
    computation.save()

    result = {"hmm_filename": hmm_name,
              "region_filename": region_filename,
              "task_id": task_id,
              "result": JobResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": JobType.VITERBI.name,
              "chromosome": chromosome,
              "ref_seq_filename": ref_seq_file,
              "wga_seq_filename": wga_seq_file,
              "no_wag_seq_filename": no_wag_seq_file,
              "viterbi_path_filename": viterbi_path_filename,
              "n_seqs": n_sequences,
              "seq_size": 0,
              "number_of_gaps": 0,
              "extracted_sequences": 1,
              "n_mixed_windows": 0}

    print("{0} Window type {1}".format(INFO, window_type))
    result["window_type"] = 'BOTH'

    # build the hmm model from the file
    hmm_model = hmm_loader.build_hmm(hmm_file=hmm_filename)

    if hmm_model is None:
        result["result"] = JobResultEnum.FAILURE.name
        result["error_explanation"] = "Could not build HMM model"
        return result

    task_id = task_id.replace('-', '_')
    hmm_path_img = VITERBI_PATHS_FILES_ROOT + task_id

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
    computation.hmm_path_img = hmm_path_img
    print("{0} Saved HMM path image {1}".format(INFO, computation.hmm_path_img))

    region = Region.load(filename=region_filename)
    region.get_mixed_windows()

    result["n_mixed_windows"] = region.get_n_mixed_windows()
    window_type = WindowType.from_string(window_type)

    try:
        sequence = region.get_region_as_rd_mean_sequences_with_windows(size=None,
                                                                       window_type=window_type,
                                                                       n_seqs=1,
                                                                       exclude_gaps=False)

        computation.extracted_sequences = 1
        result["seq_size"] = len(sequence)
        computation.seq_size = len(sequence)

        viterbi_path, observations, \
        sequence_viterbi_state = viterbi_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                     chr=chromosome, filename=viterbi_path_filename,
                                                                     append_or_write='w+')

        tuf_delete_tuf = viterbi_helpers.filter_viterbi_path(path=viterbi_path[1][1:],
                                                             wstate='TUF',
                                                             limit_state='Deletion', min_subsequence=1)

        segments = viterbi_helpers.get_start_end_segment(tuf_delete_tuf, sequence)

        filename = make_tuf_del_tuf_path_filename(task_id=task_id)
        viterbi_helpers.save_segments(segments=segments, chromosome=chromosome, filename=filename)

        # get the TUF-DEL-TUF
        tufdel.main(path=viterbi_path, fas_file_name=ref_seq_file)

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

        result["result"] = JobResultEnum.SUCCESS.name
        result["number_of_gaps"] = number_of_gaps
        computation.result = JobResultEnum.SUCCESS.name
        computation.number_of_gaps = number_of_gaps
        computation.save()
        return result
    except Exception as e:
        result["result"] = JobResultEnum.FAILURE.name
        result["number_of_gaps"] = 0
        result["error_explanation"] = str(e)
        computation.result = JobResultEnum.FAILURE.name
        computation.error_explanation = str(e)
        computation.save()
        return result






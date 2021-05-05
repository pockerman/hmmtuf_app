import ray

from compute_engine import INFO, DEFAULT_ERROR_EXPLANATION
from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine.src import hmm_loader, tufdel, viterbi_calculation_helpers as viterbi_helpers
from compute_engine.src.windows import WindowType
from compute_engine.src.region import Region


from hmmtuf import INVALID_ITEM
from hmmtuf.helpers import make_viterbi_path_filename
from hmmtuf.helpers import make_viterbi_path
from hmmtuf.helpers import make_tuf_del_tuf_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path
from hmmtuf.helpers import make_viterbi_sequence_comparison_path_filename
from hmmtuf.helpers import make_viterbi_sequence_comparison_path
from hmmtuf_home.models import RegionModel, \
    HMMModel, ViterbiSequenceModel, \
    ViterbiSequenceGroupTipModel, RegionGroupTipModel

from hmmtuf_compute.tasks_helpers import build_files_map, update_for_exception


@ray.remote
def compute_viterbi_path_task(hmm_name, chromosome, chromosome_index,
                              window_type, region_filename, hmm_filename,
                              sequence_size, n_sequences,
                              ref_seq_file, wga_seq_file, no_wga_seq_file,
                              remove_dirs, use_spade, sequence_group, scheduler_id):
    task_id = compute_viterbi_path_task.request.id
    return compute_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                chromosome=chromosome, chromosome_index=chromosome_index,
                                window_type=window_type, region_filename=region_filename,
                                hmm_filename=hmm_filename, sequence_size=sequence_size,
                                n_sequences=n_sequences, ref_seq_file=ref_seq_file,
                                wga_seq_file=wga_seq_file, no_wga_seq_file=no_wga_seq_file,
                                remove_dirs=remove_dirs, use_spade=use_spade,
                                sequence_group=sequence_group,
                                scheduler_id=scheduler_id)

def compute_viterbi_path(task_id, hmm_name, chromosome,
                         chromosome_index, window_type, region_filename,
                         hmm_filename, sequence_size, n_sequences,
                         ref_seq_file, wga_seq_file, no_wga_seq_file,
                         remove_dirs, use_spade, sequence_group, scheduler_id):
    """
    Compute the viterbi path for the given chromosome based on
    the region described in the region filename
    """

    logger.info("Computing Viterbi path")
    from .models import ViterbiComputationModel

    # get the region model from the DB
    region_model = RegionModel.objects.get(file_region=region_filename)

    viterbi_path_filename = make_viterbi_path_filename(task_id=task_id)
    task_path = make_viterbi_path(task_id=task_id)

    print("{0} task_id: {1}".format(INFO, task_id))
    print("{0} scheduler_id {1}".format(INFO, scheduler_id))
    print("{0} use_spade {1}".format(INFO, use_spade))
    print("{0} remove_dirs {1}".format(INFO, remove_dirs))

    # create a computation object in the DB
    computation = ViterbiComputationModel.build_from_data(task_id=task_id,
                                                          result=JobResultEnum.PENDING.name,
                                                          error_explanation=DEFAULT_ERROR_EXPLANATION,
                                                          file_viterbi_path=viterbi_path_filename,
                                                          region_filename=region_filename,
                                                          ref_seq_filename=ref_seq_file,
                                                          wga_seq_filename=wga_seq_file, no_wag_seq_filename=no_wga_seq_file,
                                                          hmm_filename=hmm_name,
                                                          chromosome=chromosome,
                                                          start_region_idx=region_model.start_idx,
                                                          end_region_idx=region_model.end_idx,
                                                          seq_size=0, number_of_gaps=0, hmm_path_img=None,
                                                          extracted_sequences=1, n_mixed_windows=0, window_type=window_type,
                                                          scheduler_id=scheduler_id, save=True)

    # access the created computation object
    result = ViterbiComputationModel.get_as_map(model=computation)
    result["window_type"] = 'BOTH'

    # build the hmm model from the file
    hmm_model = hmm_loader.build_hmm(hmm_file=hmm_filename)

    if hmm_model is None:
        result["result"] = JobResultEnum.FAILURE.name
        result["error_explanation"] = "Could not build HMM model"
        return result

    task_id = task_id.replace('-', '_')
    hmm_path_img = task_path

    try:
        os.mkdir(hmm_path_img)
    except OSError:

        result, computation = update_for_exception(result=result, computation=computation,
                                                   err_msg="Could not create dir: {0}".format(hmm_path_img))

        computation.save()
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
        sequence = region.get_region_as_rd_mean_sequences_with_windows(size=None, window_type=window_type,
                                                                       n_seqs=1, exclude_gaps=False)

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

        if use_spade:

            # this may fail and we  account for it
            # in the exception handler below
            os.mkdir(make_viterbi_sequence_path(task_id=task_id))

            # get the TUF-DEL-TUF i.e the repeats
            tufdel.main(path=task_path, fas_file_name=ref_seq_file,
                        chromosome=chromosome, chr_idx=chromosome_index,
                        viterbi_file=viterbi_path_filename,
                        nucleods_path=make_viterbi_sequence_path(task_id=task_id),
                        remove_dirs=remove_dirs)

            sequence = ViterbiSequenceModel()
            group = ViterbiSequenceGroupTipModel.objects.get(tip=sequence_group)
            sequence.group_tip = group
            sequence.file_sequence = make_viterbi_sequence_path_filename(task_id=task_id)
            sequence.region = region_model
            sequence.save()

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

        result, computation = update_for_exception(result=result, computation=computation,
                                                   err_msg=str(e))

        computation.save()
        return result
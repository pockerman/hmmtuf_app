"""
Celery tasks for various computations
"""
import os
from celery.decorators import task
from celery.utils.log import get_task_logger

from compute_engine import INFO, DEFAULT_ERROR_EXPLANATION
from compute_engine.job import JobType, JobResultEnum
from compute_engine import hmm_loader
from compute_engine import tufdel
from compute_engine import viterbi_calculation_helpers as viterbi_helpers
from compute_engine.windows import WindowType
from compute_engine.region import Region
from compute_engine.string_sequence_calculator import TextDistanceCalculator


from hmmtuf import INVALID_ITEM, USE_CELERY
from hmmtuf.helpers import make_viterbi_path_filename
from hmmtuf.helpers import make_viterbi_path
from hmmtuf.helpers import make_tuf_del_tuf_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path
from hmmtuf.helpers import make_viterbi_sequence_comparison_path_filename
from hmmtuf.helpers import make_viterbi_sequence_comparison_path
from hmmtuf_home.models import RegionModel, \
    HMMModel, ViterbiSequenceModel, \
    ViterbiSequenceGroupTip, RegionGroupTipModel

logger = get_task_logger(__name__)


@task(name="compute_group_viterbi_path_all_task")
def compute_group_viterbi_path_all_task(hmm_name, window_type,
                                        remove_dirs, use_spade, sequence_group):
    task_scheduler_id = compute_group_viterbi_path_all_task.request.id

    from .models import ScheduleComputation
    computation = ScheduleComputation()
    computation.task_id = task_scheduler_id
    computation.computation_type = JobType.SCHEDULE_VITERBI_GROUP_ALL_COMPUTATION.name
    computation.result = JobResultEnum.PENDING.name
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.scheduler_id = None
    computation.save()

    tips = RegionGroupTipModel.objects.all()
    result = ScheduleComputation.get_as_map(model=computation)
    result["ids"] = []
    import uuid

    try:
        for tip in tips:
            print("{0} working with tip: {1}".format(INFO, tip.tip))
            new_task_id = str(uuid.uuid4())
            result["ids"].append(new_task_id)

            compute_group_viterbi_path(task_id=new_task_id, hmm_name=hmm_name,
                                        window_type=window_type, group_tip=tip.tip,
                                        remove_dirs=remove_dirs, use_spade=use_spade,
                                        scheduler_id=task_scheduler_id, sequence_group=sequence_group)

    except Exception as e:
        computation.result = JobResultEnum.SUCCESS.name
        computation.save()
        result["result"] = JobResultEnum.SUCCESS.name
        return result

    result["result"] = JobResultEnum.SUCCESS.name
    computation.result = JobResultEnum.SUCCESS.name
    computation.save()
    return result


@task(name="compute_group_viterbi_path_task")
def compute_group_viterbi_path_task(hmm_name, window_type, group_tip,
                                    remove_dirs, use_spade, sequence_group):

    task_id = compute_group_viterbi_path_task.request.id
    return compute_group_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                      window_type=window_type, group_tip=group_tip,
                                      remove_dirs=remove_dirs, use_spade=use_spade,
                                      sequence_group=sequence_group, scheduler_id=None)


def compute_group_viterbi_path(task_id, hmm_name, window_type,  group_tip,
                               remove_dirs, use_spade, sequence_group, scheduler_id=None):

    logger.info("Computing Group Viterbi path")
    from .models import GroupViterbiComputation

    print("{0} task_id: {1}".format(INFO, task_id))
    print("{0} group_tip: {1}".format(INFO, group_tip))
    print("{0} scheduler_id {1}".format(INFO, scheduler_id))
    print("{0} use_spade {1}".format(INFO, use_spade))
    print("{0} remove_dirs {1}".format(INFO, remove_dirs))

    task_path = make_viterbi_path(task_id=task_id)

    # load the regions belonging to the same group
    # sort the regions w.r.t chromosome and region start-end
    regions = RegionModel.objects.filter(group_tip__tip=group_tip).order_by('chromosome', 'start_idx')

    # create a computation instance
    computation = GroupViterbiComputation()
    computation.task_id = task_id
    computation.computation_type = JobType.GROUP_VITERBI.name
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.hmm_filename = hmm_name
    computation.hmm_path_img = INVALID_ITEM
    computation.group_tip = group_tip
    computation.ref_seq_file = regions[0].ref_seq_file
    computation.wga_seq_filename = regions[0].wga_seq_file
    computation.no_wag_seq_filename = regions[0].no_wga_seq_file
    computation.scheduler_id = scheduler_id
    computation.number_regions = len(regions)
    computation.chromosome = regions[0].chromosome
    computation.save()

    result = GroupViterbiComputation.get_as_map(model=computation)

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

    hmm_path_img = task_path

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

    hmm_path_img = hmm_path_img + hmm_name + '.png'
    hmm_loader.save_hmm_image(hmm_model=hmm_model, path=hmm_path_img)
    computation.hmm_path_img = hmm_path_img
    result['hmm_path_img'] = hmm_path_img

    chromosome = regions[0].chromosome
    out_path = task_path + chromosome + "/"

    files_created_map = dict()
    counter_region_id = 0
    for region_model in regions:

        if counter_region_id > 1:
            continue

        region_filename = region_model.file_region.name
        region = Region.load(filename=region_filename)
        region.get_mixed_windows()

        files_created_map[counter_region_id] = {}

        #chromosome = region_model.chromosome
        chromosome_index = region_model.chromosome_index
        ref_seq_file = region_model.ref_seq_file

        # create needed directories
        try:
            # we may have many regions with the
            # same chromosome so only create once
            os.mkdir(task_path + chromosome)
        except FileExistsError as e:
            print("{0} Directory {1} exists".format(INFO, task_path + chromosome))

        path_extra = chromosome + "/" + region_model.name
        path = task_path + path_extra + "/"
        os.mkdir(path)

        viterbi_path_filename = make_viterbi_path_filename(task_id=task_id, extra_path=path_extra)
        tuf_del_tuf_filename = make_tuf_del_tuf_path_filename(task_id=task_id, extra_path=path_extra)

        try:

            # extract the sequence
            sequence = region.get_region_as_rd_mean_sequences_with_windows(size=None, window_type=window_type,
                                                                           n_seqs=1, exclude_gaps=False)

            viterbi_path, observations, \
            sequence_viterbi_state = viterbi_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                         chr=chromosome, filename=viterbi_path_filename,
                                                                         append_or_write='a')

            tuf_delete_tuf = viterbi_helpers.filter_viterbi_path(path=viterbi_path[1][1:], wstate='TUF',
                                                                 limit_state='Deletion', min_subsequence=1)

            segments = viterbi_helpers.get_start_end_segment(tuf_delete_tuf, sequence)
            viterbi_helpers.save_segments(segments=segments, chromosome=chromosome, filename=tuf_del_tuf_filename)

            if use_spade:

                if not os.path.exists(make_viterbi_sequence_path(task_id=task_id, extra_path=path_extra)):
                    os.makedirs(make_viterbi_sequence_path(task_id=task_id, extra_path=path_extra))

                # get the TUF-DEL-TUF this is for every chromosome and region
                #path = task_path + chromosome + "/" + region_model.name + "/"
                files_created = tufdel.main(path=path, fas_file_name=ref_seq_file, chromosome=chromosome,
                                            chr_idx=chromosome_index,
                                            viterbi_file=viterbi_path_filename,
                                            nucleods_path=make_viterbi_sequence_path(task_id=task_id, extra_path=path_extra),
                                            remove_dirs=remove_dirs)

                sequence = ViterbiSequenceModel()
                group = ViterbiSequenceGroupTip.objects.get(tip=sequence_group)
                sequence.group_tip = group
                sequence.file_sequence = make_viterbi_sequence_path_filename(task_id=task_id, extra_path=path_extra)
                sequence.region = region_model
                sequence.save()

                for name in files_created:
                    if name in files_created_map[counter_region_id]:
                        files_created_map[counter_region_id][name].append(path + name)
                    else:
                        files_created_map[counter_region_id][name] = [path + name]

            counter_region_id += 1
            print("{0} Done working with region: {1}".format(INFO, region_model.name))

        except Exception as e:

            result["result"] = JobResultEnum.FAILURE.name
            result["error_explanation"] = str(e)
            computation.result = JobResultEnum.FAILURE.name
            computation.error_explanation = str(e)
            computation.save()
            return result

    # only if spade is enabled do this
    if use_spade:
        try:

            for idx in files_created_map:

                names = files_created_map[idx].keys()

                for name in names:
                    print("{0} Concatenating bed {1} to {2}".format(INFO, files_created_map[idx][name], out_path + name))
                    # concatenate the files
                    tufdel.concatenate_bed_files(files_created_map[idx][name], outfile=out_path + name)
        except Exception as e:
            result["result"] = JobResultEnum.FAILURE.name
            result["error_explanation"] = str(e)
            computation.result = JobResultEnum.FAILURE.name
            computation.error_explanation = str(e)
            computation.save()
            return result

    result["result"] = JobResultEnum.SUCCESS.name
    computation.result = JobResultEnum.SUCCESS.name
    computation.save()
    print("{0} Task is finished".format(INFO))
    return result


@task(name="compute_viterbi_path_task")
def compute_viterbi_path_task(hmm_name, chromosome, chromosome_index,
                              window_type, region_filename, hmm_filename,
                              sequence_size, n_sequences,
                              ref_seq_file, wga_seq_file, no_wga_seq_file,
                              remove_dirs, use_spade, sequence_group, scheduler_id):

    task_id = compute_viterbi_path_task.request.id
    return compute_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                chromosome=chromosome,chromosome_index=chromosome_index,
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

    logger.info("Computing Viterbi path")
    from .models import ViterbiComputation

    region_model = RegionModel.objects.get(file_region=region_filename)

    viterbi_path_filename = make_viterbi_path_filename(task_id=task_id)
    task_path = make_viterbi_path(task_id=task_id)

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
    computation.no_wag_seq_filename = no_wga_seq_file
    computation.window_type = window_type
    computation.number_of_gaps = 0
    computation.seq_size = 0
    computation.n_mixed_windows = 0
    computation.extracted_sequences = 1
    computation.save()

    result = ViterbiComputation.get_as_map(model=computation)

    print("{0} Window type {1}".format(INFO, window_type))
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

        if use_spade:

            os.mkdir(make_viterbi_sequence_path(task_id=task_id))

            # get the TUF-DEL-TUF
            tufdel.main(path=task_path, fas_file_name=ref_seq_file,
                        chromosome=chromosome, chr_idx=chromosome_index,
                        viterbi_file=viterbi_path_filename,
                        nucleods_path=make_viterbi_sequence_path(task_id=task_id), remove_dirs=remove_dirs)

            sequence = ViterbiSequenceModel()
            group = ViterbiSequenceGroupTip.objects.get(tip=sequence_group)
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
        result["result"] = JobResultEnum.FAILURE.name
        result["number_of_gaps"] = 0
        result["error_explanation"] = str(e)
        computation.result = JobResultEnum.FAILURE.name
        computation.error_explanation = str(e)
        computation.save()
        return result


@task(name="compute_compare_viterbi_sequence_task")
def compute_compare_viterbi_sequence_task(distance_metric, max_num_seqs, group_tip):
    task_id = compute_compare_viterbi_sequence_task.request.id
    return compute_compare_viterbi_sequence(task_id=task_id,
                                            distance_metric=distance_metric,
                                            max_num_seqs=max_num_seqs,
                                            group_tip=group_tip)


def compute_compare_viterbi_sequence(task_id, distance_metric,
                                     max_num_seqs, group_tip):
    logger.info("Computing Viterbi sequence comparison")
    from .models import CompareViterbiSequenceComputation

    computation = CompareViterbiSequenceComputation()
    computation.task_id = task_id
    computation.result = JobResultEnum.PENDING.name
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.computation_type = JobType.VITERBI_SEQUENCE_COMPARE.name
    computation.distance_metric = distance_metric
    computation.save()

    result = CompareViterbiSequenceComputation.get_as_map(model=computation)

    tip = ViterbiSequenceGroupTip.objects.get(tip=group_tip)
    seqs = ViterbiSequenceModel.objects.filter(group_tip__tip=tip)

    if max_num_seqs != -1:

        # limit the number of sequences to do work
        seqs = seqs[0: max_num_seqs]

    seqs_filenames = []

    # collect all the sequence files
    for seq in seqs:
        seqs_filenames.append((seq.region.name, seq.file_sequence.name))

    try:

        calculator = TextDistanceCalculator(dist_type=distance_metric)

        os.mkdir(make_viterbi_sequence_comparison_path(task_id=task_id))
        calculator.calculate_from_files(fileslist=seqs_filenames,
                                        save_at=make_viterbi_sequence_comparison_path_filename(task_id=task_id),
                                        delim='\t')

        result["result"] = computation.result = JobResultEnum.SUCCESS.name
        result["file_result"] = make_viterbi_sequence_comparison_path_filename(task_id=task_id)
        computation.result = JobResultEnum.SUCCESS.name
        computation.file_result = make_viterbi_sequence_comparison_path_filename(task_id=task_id)
        computation.save()
        return result
    except Exception as e:

        result["error_explanation"] = str(e)
        result["result"] = computation.result = JobResultEnum.FAILURE.name
        computation.result = JobResultEnum.FAILURE.name
        computation.error_explanation = str(e)
        computation.save()
        return result














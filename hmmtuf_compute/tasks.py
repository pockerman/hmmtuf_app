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


@task(name="compute_group_viterbi_path_task")
def compute_group_viterbi_path_task(hmm_name, window_type, group_tip,
                                    remove_dirs, use_spade):

    task_id = compute_mutliple_viterbi_path_task.request.id
    return compute_group_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                      window_type=window_type, group_tip=group_tip,
                                      remove_dirs=remove_dirs, use_spade=use_spade)


def compute_group_viterbi_path(task_id, hmm_name, window_type,  group_tip, remove_dirs, use_spade):

    logger.info("Computing Group Viterbi path")
    from .models import GroupViterbiComputation

    task_path = make_viterbi_path(task_id=task_id)

    # load the regions belonging to the same group
    # TODO: sort the w.r.t chr and region start-end
    regions = RegionModel.objects.filter(group_tip__tip=group_tip)

    result = {"task_id": task_id,
              "result": JobResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": JobType.GROUP_VITERBI.name,
              "hmm_filename": hmm_name,
              "window_type": 'BOTH',
              'hmm_path_img': INVALID_ITEM,
              'group_tip': group_tip}

    # create a computation instance
    computation = GroupViterbiComputation()
    computation.task_id = task_id
    computation.computation_type = JobType.GROUP_VITERBI.name
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.hmm_filename = hmm_name
    computation.hmm_path_img = INVALID_ITEM
    computation.group_tip = group_tip
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

    for region_model in regions:

        region_filename = region_model.file_region.name
        region = Region.load(filename=region_filename)
        region.get_mixed_windows()

        chromosome = region_model.chromosome
        chromosome_index = region_model.chromosome_index
        ref_seq_file = region_model.ref_seq_file

        # create needed directories
        try:
            # we may have many regions with the
            # same chromosome so only create once
            os.mkdir(task_path + chromosome)
        except FileExistsError as e:
            print("{0} Directory {1} exists".format(INFO, task_path + chromosome))
            
        os.mkdir(task_path + chromosome + "/" + region_model.name)

        viterbi_path_filename = make_viterbi_path_filename(task_id=task_id,
                                                           extra_path=chromosome + "/" + region_model.name)
        tuf_del_tuf_filename = make_tuf_del_tuf_path_filename(task_id=task_id,
                                                              extra_path=chromosome + "/" + region_model.name)

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
                # get the TUF-DEL-TUF this is for every chromosome and region
                path = task_path + chromosome + "/" + region_model.name + "/"
                tufdel.main(path=path, fas_file_name=ref_seq_file, chromosome=chromosome,
                            chr_idx=chromosome_index, viterbi_file=viterbi_path_filename, remove_dirs=remove_dirs)

            print("{0} Done working with region: {1}".format(INFO, region_model.name))

        except Exception as e:

            result["result"] = JobResultEnum.FAILURE.name
            result["error_explanation"] = str(e)
            computation.result = JobResultEnum.FAILURE.name
            computation.error_explanation = str(e)
            computation.save()
            return result

    computation.result = JobResultEnum.SUCCESS.name
    computation.save()
    return result


@task(name="compute_mutliple_viterbi_path_task")
def compute_mutliple_viterbi_path_task(hmm_name, chromosome,
                                       window_type,  group_tip,
                                       ref_seq_file, wga_seq_file, no_wga_seq_file,
                                       remove_dirs, use_spade):

    task_id = compute_mutliple_viterbi_path_task.request.id
    return compute_mutliple_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                         chromosome=chromosome, window_type=window_type,
                                         group_tip=group_tip, ref_seq_file=ref_seq_file,
                                         wga_seq_file=wga_seq_file, no_wga_seq_file=no_wga_seq_file,
                                         remove_dirs=remove_dirs, use_spade=use_spade)


def compute_mutliple_viterbi_path(task_id, hmm_name, chromosome,
                                  window_type, group_tip,
                                  ref_seq_file, wga_seq_file,
                                  no_wga_seq_file, remove_dirs, use_spade):

    logger.info("Computing Multi Viterbi path")
    from .models import MultiViterbiComputation

    #import pdb
    #pdb.set_trace()

    task_path = make_viterbi_path(task_id=task_id)

    # load the regions order them by start
    regions = RegionModel.objects.filter(group_tip__tip=group_tip,
                                         chromosome=chromosome).order_by('start_idx')

    result = {"task_id": task_id,
              "result": JobResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": JobType.MULTI_VITERBI.name,
              "chromosome": chromosome,
              "ref_seq_filename": ref_seq_file,
              "wga_seq_filename": wga_seq_file,
              "no_wga_seq_filename": no_wga_seq_file,
              "hmm_filename": hmm_name,
              "file_viterbi_path": INVALID_ITEM,
              "n_regions": len(regions),
              "window_type": 'BOTH',
              'hmm_path_img': INVALID_ITEM}

    # create a computation instance
    computation = MultiViterbiComputation()
    computation.task_id = task_id
    computation.computation_type = JobType.MULTI_VITERBI.name
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.file_viterbi_path = INVALID_ITEM
    computation.chromosome = chromosome
    computation.hmm_filename = hmm_name
    computation.n_regions = len(regions)
    computation.ref_seq_filename = ref_seq_file
    computation.wga_seq_filename = wga_seq_file
    computation.no_wag_seq_filename = no_wga_seq_file
    computation.hmm_path_img = INVALID_ITEM
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
    files_created_map = dict()

    for region_model in regions:

        print("{0} Start working with region: {1}".format(INFO, region_model.name))

        region_filename = region_model.file_region.name
        region = Region.load(filename=region_filename)
        region.get_mixed_windows()

        chromosome = region_model.chromosome
        chromosome_index = region_model.chromosome_index
        ref_seq_file = region_model.ref_seq_file

        # create needed directories
        os.mkdir(task_path + region_model.name)

        # every region has its own viterbi path
        viterbi_path_filename = make_viterbi_path_filename(task_id=task_id,
                                                           extra_path=region_model.name)

        # every region has its own TUF-DEL-TUF filename
        tuf_del_tuf_filename = make_tuf_del_tuf_path_filename(task_id=task_id,
                                                              extra_path=region_model.name)
        try:

            # extract the sequence
            sequence = \
                region.get_region_as_rd_mean_sequences_with_windows(size=None, window_type=window_type,
                                                                    n_seqs=1, exclude_gaps=False)


            viterbi_path, observations, \
            sequence_viterbi_state = viterbi_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                         chr=chromosome, filename=viterbi_path_filename,
                                                                         append_or_write='a')
            #
            tuf_delete_tuf = viterbi_helpers.filter_viterbi_path(path=viterbi_path[1][1:],
                                                                 wstate='TUF',
                                                                 limit_state='Deletion', min_subsequence=1)

            segments = viterbi_helpers.get_start_end_segment(tuf_delete_tuf, sequence)
            viterbi_helpers.save_segments(segments=segments, chromosome=chromosome, filename=tuf_del_tuf_filename)

            if use_spade:

                path = task_path + region_model.name + "/"
                # get the TUF-DEL-TUF
                files_created = tufdel.main(path=path, fas_file_name=ref_seq_file,
                                            chromosome=chromosome, chr_idx=chromosome_index,
                                            viterbi_file=viterbi_path_filename, remove_dirs=remove_dirs)

                for name in files_created:

                    if name in files_created_map:
                        files_created_map[name].append(path + name)
                    else:
                        files_created_map[name] = [path + name]

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
            for name in files_created_map:

                # concatenate the files
                tufdel.concatenate_bed_files(files_created_map[name], outfile=task_path + name)
        except Exception as e:
            result["result"] = JobResultEnum.FAILURE.name
            result["error_explanation"] = str(e)
            computation.result = JobResultEnum.FAILURE.name
            computation.error_explanation = str(e)
            computation.save()
            return result

    computation.result = JobResultEnum.SUCCESS.name
    computation.save()
    return result


@task(name="compute_viterbi_path_task")
def compute_viterbi_path_task(hmm_name, chromosome, chromosome_index,
                              window_type, region_filename, hmm_filename,
                              sequence_size, n_sequences,
                              ref_seq_file, wga_seq_file, no_wga_seq_file,
                              remove_dirs, use_spade):

    task_id = compute_viterbi_path_task.request.id
    return compute_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                chromosome=chromosome,chromosome_index=chromosome_index,
                                window_type=window_type, region_filename=region_filename,
                                hmm_filename=hmm_filename, sequence_size=sequence_size,
                                n_sequences=n_sequences, ref_seq_file=ref_seq_file,
                                wga_seq_file=wga_seq_file, no_wga_seq_file=no_wga_seq_file,
                                remove_dirs=remove_dirs, use_spade=use_spade)


def compute_viterbi_path(task_id, hmm_name, chromosome,
                         chromosome_index, window_type, region_filename,
                         hmm_filename, sequence_size, n_sequences,
                         ref_seq_file, wga_seq_file, no_wga_seq_file,
                         remove_dirs, use_spade):

    logger.info("Computing Viterbi path")
    from .models import ViterbiComputation

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

    result = {"hmm_filename": hmm_name,
              "region_filename": region_filename,
              "task_id": task_id,
              "result": JobResultEnum.PENDING.name,
              "error_explanation": DEFAULT_ERROR_EXPLANATION,
              "computation_type": JobType.VITERBI.name,
              "chromosome": chromosome,
              "ref_seq_filename": ref_seq_file,
              "wga_seq_filename": wga_seq_file,
              "no_wag_seq_filename": no_wga_seq_file,
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

        if use_spade:
            # get the TUF-DEL-TUF
            tufdel.main(path=task_path, fas_file_name=ref_seq_file,
                        chromosome=chromosome, chr_idx=chromosome_index,
                        viterbi_file=viterbi_path_filename, remove_dirs=remove_dirs)

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






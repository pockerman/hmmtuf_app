"""
Celery tasks for various computations
"""
import os
from celery.decorators import task
from celery.utils.log import get_task_logger
from pathlib import Path

from compute_engine import INFO, ERROR, DEFAULT_ERROR_EXPLANATION
from compute_engine.src.enumeration_types import JobType, JobResultEnum
from compute_engine.src import hmm_loader, tufdel, viterbi_calculation_helpers as viterbi_helpers
from compute_engine.src.windows import WindowType
from compute_engine.src.region import Region
from compute_engine.src.ray_actors import ViterbiPathCalulation, SpadeCalculation
from compute_engine.src import tuf_core_helpers

from hmmtuf import INVALID_ITEM
from hmmtuf.helpers import make_viterbi_path_filename
from hmmtuf.helpers import make_viterbi_path
from hmmtuf.helpers import make_tuf_del_tuf_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path

from hmmtuf_home.models import RegionModel, \
    HMMModel, ViterbiSequenceModel, RegionGroupTipModel

from hmmtuf_compute.tasks_helpers import build_files_map, update_for_exception

logger = get_task_logger(__name__)


@task(name="compute_viterbi_path_task")
def compute_viterbi_path_task(hmm_name, chromosome, chromosome_index,
                              window_type, region_filename, hmm_filename,
                              ref_seq_file, wga_seq_file, no_wga_seq_file,
                              remove_dirs, use_spade ):
    task_id = compute_viterbi_path_task.request.id
    return compute_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                chromosome=chromosome, chromosome_index=chromosome_index,
                                window_type=window_type, region_filename=region_filename,
                                hmm_filename=hmm_filename,
                                ref_seq_file=ref_seq_file,
                                wga_seq_file=wga_seq_file, no_wga_seq_file=no_wga_seq_file,
                                remove_dirs=remove_dirs, use_spade=use_spade,)


@task(name="compute_group_viterbi_path_task")
def compute_group_viterbi_path_task(hmm_name, group_tip, remove_dirs, use_spade):
    task_id = compute_group_viterbi_path_task.request.id
    return compute_group_viterbi_path(task_id=task_id, hmm_name=hmm_name,
                                      group_tip=group_tip, remove_dirs=remove_dirs, use_spade=use_spade, )


def compute_group_viterbi_path(task_id, hmm_name, group_tip, remove_dirs, use_spade):
    """
    Compute the Viterbi paths for a group of sequences. If use_spade is True
    it also uses the SPADE application to compute the core repeats and
    concatenates the results into common files
    """

    import pdb

    logger.info("Computing Group Viterbi path")
    from .models import GroupViterbiComputationModel

    print("{0} task_id: {1}".format(INFO, task_id))
    print("{0} group_tip: {1}".format(INFO, group_tip))
    print("{0} use_spade {1}".format(INFO, use_spade))
    print("{0} remove_dirs {1}".format(INFO, remove_dirs))

    task_path = make_viterbi_path(task_id=task_id)

    # load the regions belonging to the same group
    # sort the regions w.r.t chromosome and region start-end
    regions = RegionModel.objects.filter(group_tip__tip=group_tip).order_by('chromosome', 'start_idx')
    db_group = RegionGroupTipModel.objects.get(tip=group_tip)
    db_hmm_model = HMMModel.objects.get(name=hmm_name)

    # create a computation instance
    computation = GroupViterbiComputationModel()
    computation.task_id = task_id
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.computation_type = GroupViterbiComputationModel.JOB_TYPE
    computation.hmm = db_hmm_model
    computation.group_tip = db_group
    computation.number_regions = len(regions)
    computation.start_region_idx = regions[0].start_idx
    computation.end_region_idx = regions[0].end_idx
    computation.save()

    result = GroupViterbiComputationModel.get_as_map(model=computation)

    print("{0} Result is {1}".format(INFO, result))

    actor_input = {"ref_seq_file": regions[0].ref_seq_file,
                   "chromosome": regions[0].chromosome,
                   "chromosome_idx": regions[0].chromosome_index,
                   "viterbi_path_filename": None,
                   "test_me": False,
                   "nucleods_path": None,
                   "remove_dirs": remove_dirs,
                   "hmm_model_filename": db_hmm_model.file_hmm.name,
                   "region_filename": None, }

    try:
        os.mkdir(task_path)
        print("{0} Successfully created the directory {1}".format(INFO, task_path))
    except OSError:
        result, computation = update_for_exception(result=result, computation=computation,
                                                   err_msg="Could not create dir: {0}".format(task_path))

        computation.save()
        return result

    chromosome = regions[0].chromosome
    out_path = task_path / chromosome

    files_created_map = dict()
    counter_region_id = 0

    for region_model in regions:

        print("{0} Working with region {1}".format(INFO, region_model.file_region.name))
        files_created_map[counter_region_id] = {}
        actor_input["region_filename"] = Path(region_model.file_region.name)

        # create needed directories
        try:
            # we may have many regions with the
            # same chromosome so only create once
            os.mkdir(out_path)
        except FileExistsError as e:
            print("{0} Directory {1} exists".format(INFO, out_path))

        path_extra = region_model.name
        path = out_path / path_extra

        print("{0} Creating directory {1}".format(INFO, path))
        os.mkdir(path)

        viterbi_path_filename = make_viterbi_path_filename(task_id=task_id, extra_path=chromosome + "/" + region_model.name)
        tuf_del_tuf_filename = make_tuf_del_tuf_path_filename(task_id=task_id, extra_path=chromosome + "/" + region_model.name)

        actor_input["path"] = path
        actor_input["viterbi_path_filename"] = viterbi_path_filename
        actor_input["tuf_del_tuf_filename"] = tuf_del_tuf_filename

        if use_spade:
            actor_input["nucleods_path"] = make_viterbi_sequence_path(task_id=task_id,
                                                                      extra_path=chromosome + "/" + region_model.name)
        try:

            viterbi_calculator = ViterbiPathCalulation(input=actor_input)
            viterbi_calculator.start()

            print("{0} Viterbi Output {1}".format(INFO, viterbi_calculator.output))

            if use_spade:

                spade_calculator = SpadeCalculation(input=actor_input)
                spade_calculator.start()
                print("{0} Spade calculator output {1}".format(INFO, spade_calculator.output))

                if spade_calculator.state == JobResultEnum.FAILURE:
                    print("{0} SPADE calculation errored".format(ERROR))
                    result, computation = update_for_exception(result=result,
                                                               computation=computation,
                                                               err_msg=spade_calculator.output["error_msg"])

                    computation.save()
                    return result

                files_created = spade_calculator.output["files_created"]

                build_files_map(files_created=files_created,
                                files_created_map=files_created_map,
                                counter_region_id=counter_region_id, path=path)

            counter_region_id += 1
            print("{0} Done working with region: {1}".format(INFO, region_model.name))

        except Exception as e:
            print("{0} Exception is thrown {1}".format(ERROR, str(e)))
            result, computation = update_for_exception(result=result,
                                                       computation=computation, err_msg=str(e))

            computation.save()
            return result

        # only if spade is enabled do this
    if use_spade:

        try:
            for idx in files_created_map:
                names = files_created_map[idx].keys()

                for name in names:
                    print("{0} Concatenating bed {1} to {2}".format(INFO,
                                                                        files_created_map[idx][name],
                                                                        out_path / name))
                    # concatenate the files
                    tufdel.concatenate_bed_files(files_created_map[idx][name],
                                                     outfile=out_path / name)
        except Exception as e:
            result, computation = update_for_exception(result=result, computation=computation,
                                                           err_msg=str(e))
            computation.save()
            return result

    result["result"] = JobResultEnum.SUCCESS.name
    computation.result = JobResultEnum.SUCCESS.name
    computation.save()
    print("{0} Task is finished".format(INFO))
    return result


def compute_viterbi_path(task_id, hmm_name, region_filename,
                         hmm_filename, remove_dirs, use_spade):
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
    print("{0} use_spade {1}".format(INFO, use_spade))
    print("{0} remove_dirs {1}".format(INFO, remove_dirs))

    # build the hmm model from the file
    hmm_model = hmm_loader.build_hmm(hmm_file=hmm_filename)

    import pdb
    pdb.set_trace()

    # create a computation object in the DB
    computation = ViterbiComputationModel.build_from_map(map_data={"task_id": task_id, "result": JobResultEnum.PENDING.name,
                                                          "error_explanation": DEFAULT_ERROR_EXPLANATION,
                                                          "group_tip": region_model.group_tip, "hmm": hmm_model,
                                                           "start_region_idx": region_model.start_idx,
                                                           "end_region_idx": region_model.end_idx}, save=True)

    # access the created computation object
    result = ViterbiComputationModel.get_as_map(model=computation)

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

    region = Region.load(filename=region_filename)
    region.get_mixed_windows()

    result["n_mixed_windows"] = region.get_n_mixed_windows()
    window_type = WindowType.from_string('BOTH')

    try:
        sequence = region.get_region_as_rd_mean_sequences_with_windows(size=None, window_type=window_type,
                                                                       n_seqs=1, exclude_gaps=False)

        viterbi_path, observations, \
        sequence_viterbi_state = viterbi_helpers.create_viterbi_path(sequence=sequence, hmm_model=hmm_model,
                                                                     chromosome=region.chromosome, filename=viterbi_path_filename,
                                                                     append_or_write='w+')

        tuf_delete_tuf = viterbi_helpers.filter_viterbi_path(path=viterbi_path[1][1:],
                                                             wstate='TUF', limit_state='Deletion', min_subsequence=1)

        segments = viterbi_helpers.get_start_end_segment(tuf_delete_tuf, sequence)

        filename = make_tuf_del_tuf_path_filename(task_id=task_id)
        viterbi_helpers.save_segments(segments=segments, chromosome=region.chromosome, filename=filename)

        if use_spade:

            # this may fail and we  account for it
            # in the exception handler below
            os.mkdir(make_viterbi_sequence_path(task_id=task_id))

            # get the TUF-DEL-TUF i.e the repeats
            tufdel.main(path=task_path, fas_file_name=region.ref_seq_file,
                        chromosome=region.chromosome, chr_idx=region.chromosome_index,
                        viterbi_file=viterbi_path_filename, nucleods_path=make_viterbi_sequence_path(task_id=task_id),
                        remove_dirs=remove_dirs)

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
        computation.result = JobResultEnum.SUCCESS.name
        computation.save()
        return result
    except Exception as e:

        result, computation = update_for_exception(result=result,
                                                   computation=computation, err_msg=str(e))

        computation.save()
        return result




import os
import ray
from pathlib import Path

from compute_engine import INFO, ERROR, DEFAULT_ERROR_EXPLANATION
from compute_engine.src.enumeration_types import JobResultEnum
from compute_engine.src import tufdel
from compute_engine.src.windows import WindowType
from compute_engine.src.ray_actors import ViterbiPathCalulation, SpadeCalculation

from hmmtuf.helpers import make_viterbi_path_filename
from hmmtuf.helpers import make_viterbi_path
from hmmtuf.helpers import make_tuf_del_tuf_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path_filename
from hmmtuf.helpers import make_viterbi_sequence_path

from hmmtuf_home.models import RegionModel, HMMModel, ViterbiSequenceModel, \
     RegionGroupTipModel

from hmmtuf_compute.tasks_helpers import build_files_map, update_for_exception


@ray.remote
def compute_group_viterbi_task(task_id: str, hmm_name: str,
                               group_tip: str, remove_dirs: bool, use_spade: bool):
    """
    Compute the Viterbi paths for a group of sequences. If use_spade is True
    it also uses the SPADE application to compute the core repeats and
    concatenates the results into common files
    """

    from .models import GroupViterbiComputationModel

    print("{0} task_id: {1}".format(INFO, task_id))
    print("{0} group_tip: {1}".format(INFO, group_tip))
    print("{0} use_spade {1}".format(INFO, use_spade))
    print("{0} remove_dirs {1}".format(INFO, remove_dirs))

    task_path = make_viterbi_path(task_id=task_id)

    # load the regions belonging to the same group
    # sort the regions w.r.t chromosome and region start-end
    regions = RegionModel.objects.filter(group_tip__tip=group_tip).order_by('chromosome', 'start_idx')

    # create a computation instance
    computation = GroupViterbiComputationModel()
    computation.task_id = task_id
    computation.error_explanation = DEFAULT_ERROR_EXPLANATION
    computation.result = JobResultEnum.PENDING.name
    computation.hmm_name = hmm_name
    computation.group_tip = group_tip
    computation.number_regions = len(regions)
    computation.start_region_idx = regions[0].start_idx
    computation.end_region_idx = regions[0].end_idx
    computation.save()

    result = GroupViterbiComputationModel.get_as_map(model=computation)

    db_hmm_model = HMMModel.objects.get(name=hmm_name)
    hmm_filename = db_hmm_model.file_hmm.name

    actor_input = {"ref_seq_file": None, "chromosome": regions[0].chromosome,
                   "chromosome_idx": regions[0].chromosome_idx,
                   "viterbi_path_filename": None, "test_me": False,
                   "nucleods_path": None, "remove_dirs": remove_dirs,
                   "hmm_model_filename": hmm_filename,
                   "region_filename": None}

    try:
        os.mkdir(task_path)
        print("{0} Successfully created the directory {1}".format(INFO, task_path))
    except OSError:
        result, computation = update_for_exception(result=result, computation=computation,
                                                   err_msg="Could not create dir: {0}".format(task_path))

        computation.save()
        return result

    chromosome = regions[0].chromosome
    out_path = task_path + chromosome + "/"

    files_created_map = dict()
    counter_region_id = 0

    for region_model in regions:

        print("{0} Working with region {1}".format(INFO, region_model.file_region.name))
        files_created_map[counter_region_id] = {}

        actor_input["region_filename"] = region_model.file_region
        actor_input["ref_seq_file"] = region_model.ref_seq_file
        actor_input["chromosome_idx"] = region_model.chromosome_index

        # create needed directories
        try:
            # we may have many regions with the
            # same chromosome so only create once
            os.mkdir(task_path + chromosome)
        except FileExistsError as e:
            print("{0} Directory {1} exists".format(INFO, task_path + chromosome))

        path_extra = chromosome + "/" + region_model.name
        path = task_path + path_extra + "/"

        print("{0} Creating directory {1}".format(INFO, path))
        os.mkdir(path)

        viterbi_path_filename = make_viterbi_path_filename(task_id=task_id, extra_path=path_extra)
        tuf_del_tuf_filename = make_tuf_del_tuf_path_filename(task_id=task_id, extra_path=path_extra)

        actor_input["viterbi_path_filename"] = viterbi_path_filename
        actor_input["tuf_del_tuf_filename"] = tuf_del_tuf_filename

        if use_spade:

            if not os.path.exists(make_viterbi_sequence_path(task_id=task_id, extra_path=path_extra)):
                os.makedirs(make_viterbi_sequence_path(task_id=task_id, extra_path=path_extra))

        try:
            viterbi_calculator = ViterbiPathCalulation(input=actor_input)
            viterbi_calculator.start()

            if use_spade:

                spade_calculator = SpadeCalculation(input=actor_input)
                spade_calculator.start()
                files_created = spade_calculator.output

                sequence = ViterbiSequenceModel()
                group = RegionGroupTipModel.objects.get(tip=group_tip)
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
            print("{0} Exception is thrown {1}".format(ERROR, str(e)))
            result, computation = update_for_exception(result=result,
                                                       computation=computation,
                                                       err_msg=str(e))

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
                                                                    out_path + name))
                    # concatenate the files
                    tufdel.concatenate_bed_files(files_created_map[idx][name],
                                                 outfile=out_path + name)
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
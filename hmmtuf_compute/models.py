import time
from django.db import models
from multiprocessing import Process, Manager
from json import JSONEncoder

# Create your models here.

from hmmtuf_home.utils import INFO

from . import utils
from . import region
from . import helpers
from .tasks import compute_viterbi_path_task


class ComputationEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class Computation(models.Model):

    hmm_name = None
    region_name = None
    computation_name = None
    id = None
    error = None
    error_msg = None
    finished = False
    started = False
    output = None

    @staticmethod
    def compute(computation_type, data):

        if computation_type == utils.ComputationEnum.VITERBI:

            print("Data passed: ", data)
            hmm_name = data['hmm_name']
            region_name = data['region_name']
            chromosome = data['chromosome']
            window_type = str(data['window_type'])
            viterbi_path_filename = data['viterbi_path_filename']
            region_filename = data['region_filename']
            hmm_filename = data['hmm_filename']
            sequence_size = data['sequence_size']
            n_sequences = data['n_sequences']

            # create the computation in the data base
            computation = Computation()
            computation.hmm_name = hmm_name
            computation.region_name = region_name

            return compute_viterbi_path_task.delay(hmm_name=hmm_name,
                                 chromosome=chromosome, window_type=window_type,
                                 viterbi_path_filename=viterbi_path_filename,
                                 region_filename=region_filename,
                                 hmm_filename=hmm_filename,
                                 sequence_size=sequence_size, n_sequences=n_sequences,
                                 path_img=data['path_img'])










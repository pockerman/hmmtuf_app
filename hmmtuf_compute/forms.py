from file_loader.models import HMMModel, RegionModel
from hmmtuf.settings import HMM_FILES_ROOT
from hmmtuf.settings import HMM_FILES_URL

def wrap_data_for_viterbi_calculation(request, viterbi_path_files_root):

    hmm_name = request.POST.get("hmm", '')

    hmm_model = HMMModel.objects.get(name=hmm_name)
    hmm_filename = hmm_model.file_hmm.name

    region_name = request.POST.get("region", '')
    region = RegionModel.objects.get(name=region_name)
    region_filename = region.file_region.name

    window_type = 'BOTH' #request.POST.get('window_type', '')
    chromosome = request.POST.get('chromosome', '')
    viterbi_path_filename = 'viterbi_path.txt'
    sequence_size = request.POST.get('sequence_size', None)
    n_sequences = request.POST.get('n_sequences', '')

    if n_sequences == '':
        pass
    else:
        n_sequences = int(n_sequences)

    if sequence_size == '':
        sequence_size = None
    else:
        sequence_size = int(sequence_size)

    kwargs = {'hmm_name': hmm_name,
              'region_name': region_name,
              'chromosome': chromosome,
              'window_type': window_type,
              'viterbi_path_files_root': viterbi_path_files_root,
              'viterbi_path_filename':  viterbi_path_filename,
              'region_filename': region_filename,
              'hmm_filename': hmm_filename,
              'sequence_size': sequence_size,
              'n_sequences': n_sequences,
              'path_img': viterbi_path_files_root}
    return kwargs
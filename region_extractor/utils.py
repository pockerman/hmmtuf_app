

def extract_file_names(configuration):

    reference_files_names = []
    ref_files = configuration["sequence_files"]["reference_files"]

    for i in range(len(ref_files)):
        files = configuration["sequence_files"]["reference_files"][i]

        for f in files:
            reference_files_names.extend(files[f])

    wga_files_names = []
    wga_files = configuration["sequence_files"]["wga_files"]

    for i in range(len(wga_files)):
        files = configuration["sequence_files"]["wga_files"][i]

        for f in files:
            wga_files_names.extend(files[f])

    nwga_files_names = []
    nwga_files = configuration["sequence_files"]["no_wga_files"]

    for i in range(len(nwga_files)):
        files = configuration["sequence_files"]["no_wga_files"][i]

        for f in files:
            nwga_files_names.extend(files[f])

    return reference_files_names, wga_files_names, nwga_files_names
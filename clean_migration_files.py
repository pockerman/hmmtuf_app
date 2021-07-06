import os
import shutil
from pathlib import Path

if __name__ == '__main__':
    apps = ['file_loader','hmm_creator', 'hmmtuf_compute', 'bed_comparator']

    for app_name in apps:

        if os.path.isdir(Path(app_name) / 'migrations'):
            shutil.rmtree(Path(app_name) / 'migrations')
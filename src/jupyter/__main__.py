

import subprocess
import os
from os.path import exists
from argparse import ArgumentParser


if __name__ == '__main__':
    argparser = ArgumentParser(description="""
Open a new jupyter notebook with all the public methods & classes of the pylib3d-mec-ginac
library avaliable.
""")
    argparser.add_argument(
        'file', type=str, nargs='?', help='Optional argument which indicates the filename of the notebook to run'
    )
    parsed_args = argparser.parse_args()
    file = parsed_args.file
    if file is not None and not exists(file):
        raise FileNotFoundError(f'File "{file}" not found')

    devnull = open(os.devnull, 'w')
    try:
        server = subprocess.Popen(['python', '-m', 'lib3d_mec_ginac', '--no-console'], stdout=devnull, stderr=devnull)
        jupyter_process_args = ['jupyter', 'notebook', '--KernelManager.kernel_name=lib3d-mec-ginac']
        if file is not None:
            jupyter_process_args.insert(2, file)
        jupyter_server = subprocess.Popen(jupyter_process_args, stdout=devnull, stderr=devnull)
    finally:
        devnull.close()
    try:
        server.wait()
    except KeyboardInterrupt:
        pass
    jupyter_server.kill()

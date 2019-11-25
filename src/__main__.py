'''
Author: Víctor Ruiz Gómez
Description: This script allows the user to open a python prompt in parallel with
the lib3d-mec-ginac graphical interface.
'''



from code import InteractiveConsole
from threading import Thread
import rlcompleter
import readline
from argparse import ArgumentParser


import numpy as np
import vtk
from lib3d_mec_ginac import *



class Prompt(InteractiveConsole, Thread):
    def __init__(self):
        InteractiveConsole.__init__(self, globals(), '<console>')
        Thread.__init__(self)
        self.daemon = True


    def run(self):
        # Enable tab autocomplete
        readline.parse_and_bind("tab: complete")
        # Interact interaction with the user
        self.interact(banner='', exitmsg='')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file', type=open, nargs=1, help='Python file to be executed')

    parsed_args = parser.parse_args()

    file = parsed_args.file[0]
    source = file.read()
    file.close()

    code = compile(source, '<string>', 'exec')
    exec(code, globals())


    # Run the user prompt in another thread
    prompt = Prompt()
    prompt.start()

    # Attach the scene of the default system to the viewer & run the viewer main loop
    viewer = get_viewer()
    viewer.set_scene(get_default_system().get_scene())
    viewer.main()

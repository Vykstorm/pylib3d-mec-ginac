'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Console
'''

from code import InteractiveConsole
from threading import Thread
import rlcompleter
import readline
import curses


class Console(InteractiveConsole, Thread):
    '''
    This creates a python prompt which can be executed in a secondary thread.
    '''
    def __init__(self, context):
        InteractiveConsole.__init__(self, context, '<console>')
        Thread.__init__(self)
        self.daemon = True


    def run(self):
        # Enable tab autocomplete
        readline.parse_and_bind("tab: complete")
        # Interact interaction with the user
        self.interact(banner='', exitmsg='')



if __name__ == '__main__':
    console = Console()
    console.run()

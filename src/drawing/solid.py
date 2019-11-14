'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class SolidDrawing
'''



######## Imports ########

from .stl import STLDrawing



######## class SolidDrawing ########


class SolidDrawing(STLDrawing):


    ######## Constructor ########

    def __init__(self, *args, **kwargs):
        # Validate input arguments

        
        super().__init__(*args, **kwargs)

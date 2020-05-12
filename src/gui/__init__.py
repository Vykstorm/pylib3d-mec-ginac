
from abc import ABC, abstractmethod
from tkinter import *
import tkinter.messagebox as tkMessageBox
from vtk import vtkRenderWindow
from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor
from os.path import join, dirname
import pyglet
import sys
from functools import partial, partialmethod

from lib3d_mec_ginac.core.integration import NumericIntegration

# import idle
from . import idle
sys.modules['idlelib'] = idle
from .idle.pyshell import build as build_idle, main as idle_mainloop



class GUI(ABC):
    def __init__(self, viewer):
        self._viewer = viewer
        self._initialized = False


    @property
    def _scene(self):
        return self._viewer.get_scene()

    @property
    def _simulation(self):
        return self._scene._simulation


    def build(self):
        '''build() -> vtkRenderWindowInteractor
        Builds the graphical user interface and returns an VTK interactor where the
        VTK 3D viewer is shown

        :rtype: vtkRenderWindowInteractor
        '''
        if self._initialized:
            raise RuntimeError('GUI is already built')
        iren = self._build()
        self._initialized = True
        return iren


    def main(self):
        '''main()
        Executes the main event loop of this graphical user interface. Must be invoked after
        calling :func:``build`` method
        '''
        if not self._initialized:
            raise RuntimeError('GUI must be built before executing its main event loop')
        try:
            self._main()
        finally:
            self.destroy()



    def destroy(self):
        '''destroy()
        Free the resources of this graphical user interface. Must be invoked after calling
        :func:``build`` method
        '''
        if not self._initialized:
            raise RuntimeError('GUI is not built yet')
        self._destroy()
        self._initialized = False



    @abstractmethod
    def _main(self):
        # This is the method that should be overriden by subclasses instead of ``main``
        pass


    @abstractmethod
    def _build(self):
        # This is the method that should be overriden by subclasses instead of ``build``
        pass


    def _destroy(self):
        # This is the method that should be overriden by subclasses instead of ``destroy``
        pass



class TkinterGUI(GUI):

    def _build(self):
        # Create Tk root
        tk = Tk()
        tk.title("lib3d-mec-ginac")

        # Create TK window render widget
        rw = vtkRenderWindow()
        iren = vtkTkRenderWindowInteractor(tk, rw=rw, width=600, height=600)
        iren.pack(fill='both')

        # Initialize the interactor
        iren.Initialize()

        # Save tk root, render window and interactor
        self._tk, self._iren, self._rw = tk, iren, rw

        # Return the interactor
        return iren


    def _main(self):
        tk, iren = self._tk, self._iren
        # Start the interactor
        iren.Start()

        # Start TK main loop
        tk.mainloop()



    def _destroy(self):
        iren, rw = self._iren, self._rw

        # Clean up resources when finished
        rw.Finalize()
        del self._rw, self._iren, self._tk
        iren.SetRenderWindow(None)
        iren.TerminateApp()




class DefaultGUI(TkinterGUI):
    # This is the default GUI used to display the 3D viewer
    pass




class IDEGUI(DefaultGUI):
    # This is the GUI that integrates the 3D viewer with IDLE


    def _load_fonts(self):
        pyglet.font.add_file(join(dirname(__file__), 'fonts', 'Lucida Console Regular.ttf'))


    def _start_stop_simulation_menu_clicked(self):
        simulation = self._simulation
        if simulation.is_stopped():
            simulation.start()
        else:
            simulation.stop()


    def _pause_resume_simulation_menu_clicked(self):
        simulation = self._simulation
        if simulation.is_stopped():
            tkMessageBox.showwarning('Warning', 'Simulation was not started yet', parent=self._tk)
            return
        if simulation.is_running():
            simulation.pause()
        else:
            simulation.resume()




    def _adjust_idle_widgets(self, top_level):
        # Modify column & row number labels position ( of the console prompt )
        bar = top_level.children['!multistatusbar']
        col_number_label = bar.children['!label']
        line_number_label = bar.children['!label2']

        line_number_label.pack(side='left')
        col_number_label.pack(side='left')


    def _build_num_integration_menu(self, menu):
        # Create submenu to change the numeric integration method for the simulation
        num_integration_menu = Menu(menu, tearoff=False)
        for method in NumericIntegration.get_methods():
            num_integration_menu.add_radiobutton(
                label=method.__name__,
                value=method.__name__,
                command=partial(self._simulation.set_integration_method, method)
            )
        return num_integration_menu


    def _build_delta_time_menu(self, menu):
        # Create submenu to change the delta time for the simulation
        delta_time_menu = Menu(menu, tearoff=False)
        for value in (0.1, 0.05, 0.02, 0.01):
            delta_time_menu.add_radiobutton(
                label=str(value),
                value=value,
                command=partial(self._simulation.set_delta_time, value)
            )
        return delta_time_menu



    def _build_refresh_rate_menu(self, menu):
        # This creates a submenu to change the refresh rate of the graphics
        refresh_rate_menu = Menu(menu, tearoff=False)
        for value in (30, 20, 10):
            refresh_rate_menu.add_radiobutton(
                label=str(value),
                value=value,
                command=partial(self._viewer.set_drawing_refresh_rate, value)
            )

        return refresh_rate_menu



    def _build_simulation_menu(self, menu):
        # This function builds the "simulation" menu

        # Build submenus
        num_integration_menu = self._build_num_integration_menu(menu)
        delta_time_menu = self._build_delta_time_menu(menu)
        refresh_rate_menu = self._build_refresh_rate_menu(menu)

        menu.add_command(label='Start/Stop', command=self._start_stop_simulation_menu_clicked)
        menu.add_command(label='Pause/Resume', command=self._pause_resume_simulation_menu_clicked)
        menu.add_separator()
        menu.add_cascade(label='Set integration method', menu=num_integration_menu)
        menu.add_cascade(label='Set delta time', menu=delta_time_menu)
        menu.add_cascade(label='Set refresh rate', menu=refresh_rate_menu)
        display_simulation_info_var = BooleanVar(master=self._tk, value=True)
        menu.add_checkbutton(
            label='Display simulation info',
            var=display_simulation_info_var,
            command=lambda: self._scene.toogle_drawings(simulation_info=display_simulation_info_var.get())
        )



    def _build_scene_menu(self, menu):
        # Add submenus to the menu "scene"

        drawing_types = ('points', 'vectors', 'frames', 'solids', 'grid', 'decorations')
        states = [BooleanVar(master=self._tk, value=True) for i in range(len(drawing_types))]

        def drawing_visibility_changed(drawing_type, state):
            if drawing_type == 'decorations':
                drawing_type = 'others'
            self._scene.toogle_drawings(**{drawing_type: state.get()})

        for drawing_type, state in zip(drawing_types, states):
            menu.add_checkbutton(
                label=f'Draw {drawing_type}',
                var=state,
                command=partial(drawing_visibility_changed, drawing_type, state)
            )
        menu.add_separator()
        menu.add_command(label='Purge drawings', command=self._scene.purge_drawings)






    def _build_menus(self, menu_bar):
        # Add extra submenus for the "simulation" menu
        self._build_simulation_menu(menu_bar.children['simulation'])

        # Add extra submenus for the "scene" menu
        self._build_scene_menu(menu_bar.children['scene'])





    def _build(self):
        # Build IDLE
        tk = build_idle()
        self._tk = tk
        top_level = tk.children['!listedtoplevel']
        menu_bar = tk.children['!menu']

        # Build extra widgets for IDLE
        self._load_fonts()
        self._build_menus(menu_bar)
        self._adjust_idle_widgets(top_level)

        # Update GUI
        tk.update()

        # Create TK window render widget
        rw = vtkRenderWindow()
        iren = vtkTkRenderWindowInteractor(top_level, width=600, height=600, rw=rw)
        iren.pack(expand=True, side='right', fill='both')

        # Initialize the interactor
        iren.Initialize()

        # Save render window and interactor
        self._iren, self._rw = iren, rw

        # Return the interactor
        return iren



    def _main(self):
        # Start the interactor
        self._iren.Start()

        # Execute idle mainloop
        idle_mainloop()

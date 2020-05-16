
from abc import ABC, abstractmethod
from tkinter import *
import tkinter.messagebox as tkMessageBox
from vtk import vtkRenderWindow
from os.path import join, dirname
import sys
from functools import partial, partialmethod, lru_cache
import webbrowser
from copy import copy

from ..core.integration import NumericIntegration
from ..core.system import get_default_system, set_default_system, System
from ..drawing.events import EventProducer
from ..drawing.scene import Scene

# Only import pyglet if python is <= 3.7.4
# See bug: https://stackoverflow.com/questions/59892863/python-error-typeerror-item-1-in-argtypes-passes-a-union-by-value-which-is
from sys import version_info
if version_info.minor <= 7 and version_info.micro <= 4:
    try:
        import pyglet
    except ImportError:
        pass


# import idle
from . import idle
sys.modules['idlelib'] = idle





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
        self._main()




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
        from tkinter import Tk
        from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

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
        tk, iren, rw = self._tk, self._iren, self._rw

        # Clean up resources when finished
        rw.Finalize()
        del self._rw, self._iren, self._tk
        iren.SetRenderWindow(None)
        iren.TerminateApp()
        #tk.destroy()




class DefaultGUI(TkinterGUI):
    # This is the default GUI used to display the 3D viewer
    pass




class IDEGUI(DefaultGUI, EventProducer):
    # This is the GUI that integrates the 3D viewer with IDLE


    _delta_time_values = (0.1, 0.05, 0.02, 0.01)
    _refresh_rate_values = (30, 20, 10)


    def __init__(self, viewer):
        DefaultGUI.__init__(self, viewer)
        EventProducer.__init__(self)
        self._drawings_visibility_groups_menu_vars = {}
        self.add_child(viewer)



    def _load_fonts(self):
        try:
            pyglet.font.add_file(join(dirname(__file__), 'fonts', 'Lucida Console Regular.ttf'))
        except NameError:
            pass


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


    def _open_api_docs(self):
        webbrowser.open('https://pylib3d-mec-ginac-docs.herokuapp.com/')


    def _open_help_about(self):
        # TODO
        pass





    def _adjust_idle_widgets(self, top_level):
        # Modify column & row number labels position ( of the console prompt )
        bar = top_level.children['!multistatusbar']
        col_number_label = bar.children['!label']
        line_number_label = bar.children['!label2']

        line_number_label.pack(side='left')
        col_number_label.pack(side='left')


    def _update_menus(self):
        simulation, scene = self._simulation, self._scene

        # Update numeric integration radiobutton state
        self._num_integration_menu_var.set(simulation.get_integration_method_name())

        # Update delta time radiobutton menu state
        try:
            self._delta_time_menu_var.set(self._delta_time_values.index(simulation.get_delta_time()))
        except ValueError:
            self._delta_time_menu_var.set(-1)

        # Update refresh rate radiobutton menu state
        try:
            self._refresh_rate_menu_var.set(self._refresh_rate_values.index(self._viewer.get_drawing_refresh_rate()))
        except ValueError:
            self._refresh_rate_menu_var.set(-1)

        # Update checkboxes state ( drawings visibility by type )
        for drawing_type, var in self._drawings_visibility_groups_menu_vars.items():
            try:
                var.set(scene.get_drawings_group_visibility(drawing_type))
            except ValueError:
                var.set(False)




    def _build_num_integration_menu(self, menu):
        # Create submenu to change the numeric integration method for the simulation
        num_integration_menu = Menu(menu, tearoff=False)
        num_integration_menu_var = StringVar(master=self._tk)

        def update_integration_method(method):
            self._simulation.set_integration_method(method)

        for method in NumericIntegration.get_methods():
            num_integration_menu.add_radiobutton(
                label=method.__name__,
                value=method.__name__,
                var=num_integration_menu_var,
                command=partial(update_integration_method, method)
            )

        self._num_integration_menu_var = num_integration_menu_var
        return num_integration_menu


    def _build_delta_time_menu(self, menu):
        # Create submenu to change the delta time for the simulation
        delta_time_menu_var = IntVar(master=self._tk)
        delta_time_menu = Menu(menu, tearoff=False)

        def update_delta_time(value):
            self._simulation.set_delta_time(value)

        for i, value in enumerate(self._delta_time_values):
            delta_time_menu.add_radiobutton(
                label=str(value),
                value=i,
                var=delta_time_menu_var,
                command=partial(update_delta_time, value)
            )

        self._delta_time_menu_var = delta_time_menu_var

        return delta_time_menu



    def _build_refresh_rate_menu(self, menu):
        # This creates a submenu to change the refresh rate of the graphics
        refresh_rate_menu_var = IntVar(master=self._tk)
        refresh_rate_menu = Menu(menu, tearoff=False)

        for i, value in enumerate(self._refresh_rate_values):
            refresh_rate_menu.add_radiobutton(
                label=str(value),
                value=i,
                var=refresh_rate_menu_var,
                command=partial(self._viewer.set_drawing_refresh_rate, value)
            )

        self._refresh_rate_menu_var = refresh_rate_menu_var

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
        display_simulation_info_var = BooleanVar(master=self._tk)
        menu.add_checkbutton(
            label='Display simulation info',
            var=display_simulation_info_var,
            command=lambda: self._scene.toogle_drawings(simulation_info=display_simulation_info_var.get())
        )
        self._drawings_visibility_groups_menu_vars['simulation_info'] = display_simulation_info_var



    def _build_scene_menu(self, menu):
        # Add submenus to the menu "scene"
        drawing_groups = ('points', 'vectors', 'frames', 'solids', 'grid', 'others')
        states = dict(zip(
            drawing_groups,
            [BooleanVar(master=self._tk) for group in drawing_groups]
        ))
        self._drawings_visibility_groups_menu_vars.update(states)


        def drawing_visibility_changed(drawing_type, state):
            self._scene.toogle_drawings(**{drawing_type: state.get()})

        for drawing_type, state in states.items():
            menu.add_checkbutton(
                label=f'Draw {drawing_type if drawing_type != "others" else "decorations"}',
                var=state,
                command=partial(drawing_visibility_changed, drawing_type, state)
            )
        menu.add_separator()
        menu.add_command(label='Purge drawings', command=lambda: self._scene.purge_drawings())



    def _build_help_menu(self, menu):
        # Add submenu to open the docs of lib3d-mec-ginac
        menu.add_command(label='lib3d-mec-ginac docs', command=self._open_api_docs)

        # Add submenu to show license, authors info, ...
        menu.add_separator()
        menu.add_command(label='About', command=self._open_help_about)




    def _build_menus(self, menu_bar):
        # Add extra submenus for the "simulation" menu
        self._build_simulation_menu(menu_bar.children['simulation'])

        # Add extra submenus for the "scene" menu
        self._build_scene_menu(menu_bar.children['scene'])

        # Add extra submenus for the "help" menu
        self._build_help_menu(menu_bar.children['help'])

        # Update menus
        self._update_menus()



    def _build(self):
        from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor
        from .idle.pyshell import build as build_idle, main as idle_mainloop


        # Build IDLE
        tk = build_idle(self)
        self._tk = tk
        top_level = tk.children['!listedtoplevel']
        menu_bar = tk.children['!menu']

        # Build extra widgets for IDLE
        self._load_fonts()
        self._build_menus(menu_bar)
        self._adjust_idle_widgets(top_level)

        # Add event handlers
        self._add_event_handlers()

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
        from .idle.pyshell import main as idle_mainloop

        # Start the interactor
        self._iren.Start()

        # Execute idle mainloop
        idle_mainloop()


    def _destroy(self):
        self._remove_event_handlers()
        self._drawings_visibility_groups_menu_vars.clear()
        super()._destroy()






    def _add_event_handlers(self):
        # This will add all the handlers that will listen for events in the 3D viewer
        self.add_event_handler(self._on_event)



    def _remove_event_handlers(self):
        # This method will remove all the event handlers previously attached to the 3D viewer
        self.remove_event_handler(self._on_event)


    def _on_event(self, event_type, *args, **kwargs):
        # This method delegates events calling to the correct handler for each kind of event
        try:
            handler = getattr(self, f'_on_{event_type}')
            handler(*args, **kwargs)
        except AttributeError:
            pass



    def _on_delta_time_changed(self, *args, **kwargs):
        # Handler called when delta time changes
        delta_t = self._simulation.get_delta_time()
        var = self._delta_time_menu_var
        try:
            var.set(self._delta_time_values.index(delta_t))
        except ValueError:
            var.set(-1)


    def _on_drawing_refresh_rate_changed(self, *args, **kwargs):
        # Handler called when simulation graphics refresh rate
        rate = self._viewer.get_drawing_refresh_rate()
        var = self._refresh_rate_menu_var
        try:
            var.set(self._refresh_rate_values.index(rate))
        except ValueError:
            var.set(-1)


    def _on_integration_method_changed(self, *args, **kwargs):
        self._num_integration_menu_var.set(self._simulation.get_integration_method_name())


    def _on_drawings_group_visibility_changed(self, source, drawing_type, visible):
        try:
            self._drawings_visibility_groups_menu_vars[drawing_type].set(visible)
        except KeyError:
            pass


    def _on_shell_restart(self, *args, **kwargs):
        # Change default system
        set_default_system(System())
        self._viewer.set_scene(get_default_system().get_scene())

        # Restore default global variables
        main_module = sys.modules['__main__']
        if '_default_environment' in globals():
            main_module.__dict__.clear()
            main_module.__dict__.update(_default_environment)

        # Update menu checkboxes & radiobuttons states
        self._update_menus()

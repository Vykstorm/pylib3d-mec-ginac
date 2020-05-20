
API Reference
-----------------------------------

The API is composed by a set of classses & routines which can be imported from this package with::

    from lib3d_mec_ginac import *





.. currentmodule:: lib3d_mec_ginac


Core module
============================


.. autoclass:: System
    :members:
        O,
        abs,
        acceleration_vector,
        accelerations,
        angular_acceleration,
        angular_velocity,
        angular_velocity_tensor,
        autogen_latex_names,
        aux_accelerations,
        aux_coordinates,
        aux_coords,
        aux_velocities,
        bases,
        compile_numeric_func,
        compile_numeric_func_c_optimized,
        compile_numeric_function,
        compile_numeric_function_c_optimized,
        coordinates,
        coords,
        derivative,
        diff,
        dt,
        evaluate,
        export_numeric_func_MATLAB,
        export_numeric_function_MATLAB,
        export_numeric_init_func_MATLAB,
        export_numeric_init_function_MATLAB,
        fire_event,
        frames,
        get_acc,
        get_acceleration,
        get_accelerations,
        get_accelerations_matrix,
        get_accelerations_values,
        get_aux_acc,
        get_aux_acceleration,
        get_aux_accelerations,
        get_aux_accelerations_matrix,
        get_aux_accelerations_values,
        get_aux_coord,
        get_aux_coordinate,
        get_aux_coordinates,
        get_aux_coordinates_matrix,
        get_aux_coordinates_values,
        get_aux_coords,
        get_aux_coords_matrix,
        get_aux_coords_values,
        get_aux_vel,
        get_aux_velocities,
        get_aux_velocities_matrix,
        get_aux_velocities_values,
        get_aux_velocity,
        get_base,
        get_bases,
        get_coord,
        get_coordinate,
        get_coordinates,
        get_coordinates_matrix,
        get_coordinates_values,
        get_coords,
        get_coords_matrix,
        get_coords_values,
        get_frame,
        get_frames,
        get_input,
        get_inputs,
        get_inputs_matrix,
        get_inputs_values,
        get_joint_unknown,
        get_joint_unknowns,
        get_joint_unknowns_matrix,
        get_joint_unknowns_values,
        get_matrices,
        get_matrix,
        get_param,
        get_parameter,
        get_parameters,
        get_parameters_matrix,
        get_parameters_values,
        get_params,
        get_params_matrix,
        get_params_values,
        get_point,
        get_points,
        get_scene,
        get_solid,
        get_solids,
        get_symbol,
        get_symbols,
        get_symbols_matrix,
        get_symbols_values,
        get_tensor,
        get_tensors,
        get_time,
        get_unknown,
        get_unknowns,
        get_unknowns_matrix,
        get_unknowns_values,
        get_value,
        get_values,
        get_vector,
        get_vectors,
        get_vel,
        get_velocities,
        get_velocities_matrix,
        get_velocities_values,
        get_velocity,
        get_wrench,
        get_wrenches,
        gravity_wrench,
        has_acc,
        has_acceleration,
        has_aux_acc,
        has_aux_acceleration,
        has_aux_coord,
        has_aux_coordinate,
        has_aux_vel,
        has_aux_velocity,
        has_base,
        has_coord,
        has_coordinate,
        has_frame,
        has_input,
        has_joint_unknown,
        has_matrix,
        has_param,
        has_parameter,
        has_point,
        has_solid,
        has_symbol,
        has_tensor,
        has_unknown,
        has_vector,
        has_vel,
        has_velocity,
        has_wrench,
        inertia_wrench,
        inputs,
        jacobian,
        joint_unknowns,
        matrices,
        new_aux_coord,
        new_aux_coordinate,
        new_base,
        new_coord,
        new_coordinate,
        new_frame,
        new_input,
        new_joint_unknown,
        new_matrix,
        new_param,
        new_parameter,
        new_point,
        new_solid,
        new_symbol,
        new_tensor,
        new_unknown,
        new_vector,
        new_wrench,
        parameters,
        params,
        points,
        position_vector,
        pre_point_branch,
        previous_point_branch,
        reduced_base,
        reduced_point,
        restore_previous_state,
        rotation_matrix,
        save_state,
        scene,
        set_as_default,
        set_value,
        solids,
        symbols,
        tensors,
        time,
        to_symbol,
        twist,
        unknowns,
        vectors,
        velocities,
        velocity_vector,
        wrenches,
        xyz


.. autoclass:: AssemblyProblemSolver
    :members:
        __init__,
        init,
        step


.. autoclass:: NumericIntegration
    :members:
        euler,
        rk4,
        get_method,
        get_methods





Symbolic algebra
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: SymbolNumeric
    :members:
        get_owner,
        get_tex_name,
        get_type,
        get_value,
        kind,
        owner,
        set_tex_name,
        set_value,
        tex_name,
        type,
        value



.. autoclass:: Expr
    :members:
        as_symbol,
        eval,
        is_symbol,
        to_symbol



.. autoclass:: Matrix
    :members:
         __len__,
        __getitem__,
        __setitem__,
        __iter__,
        __reversed__,
        T,
        are_all_values_symbols,
        block,
        eye,
        get,
        get_num_cols,
        get_num_rows,
        get_shape,
        get_size,
        get_transposed,
        get_values,
        get_values_as_symbols,
        num_cols,
        num_rows,
        rot,
        set,
        shape,
        size,
        subs,
        transpose,
        transposed,
        values,
        xrot,
        yrot,
        zrot


.. autoclass:: NumericFunction
    :members:
        get_atoms,
        get_outputs,
        get_globals,
        load_from_file,
        save_to_file,
        evaluate,
        atoms,
        outputs,
        globals,
        __call__




Geometric entities
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Vector3D
    :members:
        get_module,
        get_skew,
        in_base,
        dot,
        cross,
        normalize,
        module,
        normalized,
        skew,
        x,
        y,
        z


.. autoclass:: Tensor3D
    :members:
        in_base


.. autoclass:: Base
    :members:
        get_previous_base,
        has_previous_base,
        get_rotation_angle,
        get_rotation_tupla,
        previous_base,
        previous,
        rotation_angle,
        rotation_tupla,
        get_previous,
        has_previous


.. autoclass:: Point
    :members:
        get_position_vector,
        get_position,
        get_previous,
        has_previous,
        position_vector,
        position,
        previous


.. autoclass:: Frame
    :members:
        get_scale,
        set_point,
        point,
        scale



.. autoclass:: Wrench3D
    :members:
        get_force,
        get_moment,
        get_solid,
        get_type,
        get_point,
        unatomize,
        at_point,
        force,
        moment,
        solid,
        type,
        point


.. autoclass:: Solid
    :members:
        get_CM,
        get_IT,
        get_G,
        get_mass,
        CM,
        IT,
        G,
        mass





Drawing module
============================

.. autoclass:: Scene
    :members:

.. autoclass:: VtkViewer
    :members:


Drawings
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Drawing
    :members:


.. autoclass:: Drawing2D
    :members:


.. autoclass:: Drawing3D
    :members:


.. autoclass:: TextDrawing
    :members:


.. autoclass:: PointDrawing
    :members:


.. autoclass:: VectorDrawing
    :members:

.. autoclass:: FrameDrawing
    :members:


.. autoclass:: PositionVectorDrawing
    :members:


.. autoclass:: VelocityVectorDrawing
    :members:

.. autoclass:: SolidDrawing
    :members:



Geometry meshes
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Sphere
    :members:


.. autoclass:: Cube
    :members:


.. autoclass:: Cone
    :members:


.. autoclass:: Cylinder
    :members:


.. autoclass:: Line
    :members:


.. autoclass:: LineStrip
    :members:



Affine transformations
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Transform
    :members:





Global functions
============================

.. autofunction:: get_default_system

.. autofunction:: set_default_system

.. autofunction:: set_atomization_state

.. autofunction:: enable_atomization

.. autofunction:: disable_atomization

.. autofunction:: get_atomization_state

.. autofunction:: set_gravity_direction

.. autofunction:: set_gravity_up

.. autofunction:: set_gravity_down

.. autofunction:: get_gravity_direction

.. autofunction:: unatomize

.. autofunction:: subs

.. autofunction:: evaluate

.. autofunction:: print_latex

.. autofunction:: to_latex





Mathematical functions
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: dot

.. autofunction:: cross

.. autofunction:: sin

.. autofunction:: cos

.. autofunction:: tan

.. autofunction:: sqrt




Graphics utility functions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: scad_to_stl

.. autofunction:: read_stl

.. autofunction:: write_stl

.. autofunction:: get_viewer

.. autofunction:: open_viewer

.. autofunction:: get_selected_drawing

.. autofunction:: set_drawing_refresh_rate

.. autofunction:: get_drawing_refresh_rate

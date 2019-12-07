
API Reference
-----------------------------------


.. currentmodule:: lib3d_mec_ginac

.. autoclass:: System
    :members:
        get_value, set_value,
        get_symbol,
        get_time,
        get_coordinate, get_velocity, get_acceleration,
        get_aux_coordinate, get_aux_velocity, get_aux_acceleration,
        get_parameter, get_joint_unknown, get_input,
        get_base, get_matrix, get_vector, get_tensor,
        get_point, get_frame, get_solid, get_wrench,
        has_symbol,
        has_coordinate, has_velocity, has_acceleration,
        has_aux_coordinate, has_aux_velocity, has_aux_acceleration,
        has_parameter, has_joint_unknown, has_input,
        has_base, has_matrix, has_vector, has_tensor,
        has_point, has_frame, has_solid, has_wrench,
        get_symbols,
        get_coordinates, get_velocities, get_accelerations,
        get_aux_coordinates, get_aux_velocities, get_aux_accelerations,
        get_parameters, get_joint_unknowns, get_inputs,
        get_bases, get_matrices, get_vectors, get_tensors,
        get_points, get_frames, get_solids, get_wrenches,
        get_symbols_matrix,
        get_coordinates_matrix, get_velocities_matrix, get_accelerations_matrix,
        get_aux_coordinates_matrix, get_aux_velocities_matrix, get_aux_accelerations_matrix,
        get_parameters_matrix, get_joint_unknowns_matrix, get_inputs_matrix,
        get_scene,
        new_parameter, new_joint_unknown, new_input,
        new_coordinate, new_aux_coordinate, new_symbol,
        new_base, new_matrix, new_vector, new_tensor,
        new_point, new_frame, new_solid, new_wrench,
        reduced_base, reduced_point, pre_point_branch,
        rotation_matrix, position_vector,
        angular_velocity, angular_velocity_tensor, velocity_vector,
        angular_acceleration, acceleration_vector,
        twist, derivative, jacobian, diff,
        gravity_wrench, inertia_wrench,
        symbols,
        time,
        coordinates, velocities, accelerations,
        aux_coordinates, aux_velocities, aux_accelerations,
        parameters, inputs, joint_unknowns,
        bases, matrices, vectors, tensors,
        points, frames, solids, wrenches,
        O, abs, xyz,
        evaluate,
        autogen_latex_names,
        set_as_default,
        scene



.. autoclass:: SymbolNumeric
    :members:
        get_value, get_tex_name, get_owner, get_type,
        set_value, set_tex_name,
        value, tex_name, owner, type,
        __float__, __int__, __complex__



.. autoclass:: Matrix
    :members:
        block,
        get_shape, get_num_rows, get_num_cols, get_size, __len__,
        get_values, get, __getitem__,
        __iter__, __reversed__,
        set,
        transpose, subs,
        get_numeric_function, get_numeric_func,
        shape, num_rows, num_cols, size, T, transposed, values,
        numeric_function, numeric_func,
        eye, xrot, yrot, zrot



.. autoclass:: Vector3D
    :members:
        get_module, get_skew, in_base, dot, cross, normalize,
        module, skew, x, y, z, normalized


.. autoclass:: Tensor3D
    :members:
        in_base

.. autoclass:: Base
    :members:
        get_previous_base, has_previous_base,
        get_rotation_angle, get_rotation_tupla,
        previous_base, rotation_angle, rotation_tupla

.. autoclass:: Point
    :members:
        get_position_vector, get_previous, has_previous,
        position_vector, previous


.. autoclass:: Frame
    :members:
        get_point, get_scale, set_point,
        point, scale


.. autoclass:: Solid
    :members:
        get_CM, get_IT, get_mass,
        CM, IT, mass

.. autoclass:: Wrench3D
    :members:
        get_force, get_moment, get_solid, get_type, get_point,
        force, moment, solid, type, point


.. autoclass:: NumericFunction
    :members:
        get_atoms, get_outputs, get_globals,
        load_from_file, save_to_file,
        __call__


.. autoclass:: Scene
    :members:
        is_simulation_running, is_simulation_paused, is_simulation_stopped,
        get_simulation_update_frequency, get_simulation_time_multiplier,
        get_simulation_real_update_frequency,
        get_drawings, get_2D_drawings, get_3D_drawings,
        get_background_color, get_render_mode,
        set_simulation_update_frequency, set_simulation_time_multiplier,
        set_background_color, set_render_mode,
        start_simulation, stop_simulation, resume_simulation, pause_simulation,
        purge_drawings, add_drawing,
        draw_point, draw_frame, draw_vector, draw_stl, draw_scad, draw_solid,
        draw_position_vector, draw_velocity_vector,
        draw_text,
        background_color, render_mode




.. autoclass:: lib3d_mec_ginac.drawing.viewer.VtkViewer
    :members:
        open, close,
        is_open, is_closed,
        set_title



.. autoclass:: Drawing3D
    :members:
        get_geometry, set_geometry,
        get_transform, set_transform, clear_transform,
        rotate, scale, translate, rotate_to_dir,
        show, hide,
        get_color, set_color,
        transform, color



.. autoclass:: Transform
    :members:
        evaluate, concatenate,
        identity, translation, rotation, scale, rotation_from_dir,
        __and__






Global functions
==========================

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




Mathematic functions
~~~~~~~~~~~~~~~~~~~~


.. autofunction:: dot

.. autofunction:: cross

.. autofunction:: sin

.. autofunction:: cos

.. autofunction:: tan

.. autofunction:: sqrt




Drawing utility functions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: scad_to_stl

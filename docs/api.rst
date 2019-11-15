
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
        evaluate,
        autogen_latex_names,
        set_as_default



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
        get_rotation_angle, get_rotation_tupla, get_rotation,
        previous_base, rotation_angle, rotation_tupla, rotation

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


.. autoclass:: Viewer
    :members:
        get_simulation_update_frequency, get_simulation_update_freq,
        get_simulaton_time_multiplier,
        is_simulation_running, is_simulation_paused, is_simulation_stopped,
        are_drawings_shown,
        get_simulation_elapsed_time,
        set_simulation_update_frequency, set_simulation_time_multiplier,
        draw_point, draw_frame, draw_solid, draw_vector,
        show_drawings, hide_drawings,
        start_simulation, stop_simulation, pause_simulation, resume_simulation,
        simulation_update_frequency, simulation_time_multiplier





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


from math import sin, cos, tan
import numpy as np
cimport numpy as np

cpdef evaluate(np.ndarray[np.float64_t, ndim=2] acceleration, np.ndarray[np.float64_t, ndim=2] joint_unknown, np.ndarray[np.float64_t, ndim=2] coordinate, np.ndarray[np.float64_t, ndim=2] input, np.ndarray[np.float64_t, ndim=2] aux_velocity, np.ndarray[np.float64_t, ndim=2] parameter, np.ndarray[np.float64_t, ndim=2] aux_coordinate, np.ndarray[np.float64_t, ndim=2] velocity, np.ndarray[np.float64_t, ndim=2] aux_acceleration, np.ndarray[np.float64_t, ndim=2] __output__):
	cdef np.float64_t atom1 = parameter[2, 0]**2
	cdef np.float64_t atom0 = parameter[3, 0]**2
	cdef np.float64_t atom5 = parameter[1, 0]**2
	cdef np.float64_t atom4 = parameter[1, 0]*parameter[3, 0]
	cdef np.float64_t atom3 = parameter[1, 0]*parameter[2, 0]
	cdef np.float64_t atom7 = parameter[2, 0]*parameter[3, 0]
	cdef np.float64_t atom34 = (atom1+atom0+atom5)**(1/2)
	cdef np.float64_t atom10 = -atom4*parameter[2, 0]
	cdef np.float64_t atom9 = atom3*parameter[3, 0]
	cdef np.float64_t atom6 = -atom0-atom5
	cdef np.float64_t atom8 = -atom1-atom5
	cdef np.float64_t atom2 = -atom1-atom0
	cdef np.float64_t atom21 = parameter[1, 0]*atom7
	__output__[0, 0] = atom34*(atom10+atom9)
	__output__[0, 1] = (parameter[1, 0]*atom4-atom2*parameter[3, 0])*atom34
	__output__[0, 2] = atom34*(parameter[2, 0]*atom2-parameter[1, 0]*atom3)
	__output__[1, 0] = atom34*(atom6*parameter[3, 0]-atom7*parameter[2, 0])
	__output__[1, 1] = -atom34*(atom9-atom21)
	__output__[1, 2] = atom34*(parameter[2, 0]*atom3-parameter[1, 0]*atom6)
	__output__[2, 0] = (atom7*parameter[3, 0]-parameter[2, 0]*atom8)*atom34
	__output__[2, 1] = atom34*(parameter[1, 0]*atom8-atom4*parameter[3, 0])
	__output__[2, 2] = -(atom10+atom21)*atom34
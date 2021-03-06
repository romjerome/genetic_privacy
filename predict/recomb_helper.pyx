# cython: profile=True

from diploid import Diploid

import numpy as np

cimport numpy as np
cimport cython

def new_sequence(diploid, locations):
    """
    Return a new sequence, broken up at the given start, stop locations.
    Eg the sequence starts: 0  10 20
                    stops:  10 20 30
    passed with the locations [15, 25] should produce the sequence
                    starts: 0  10 15 20 25
                    stops:  10 15 20 25 30
    """
    cdef np.ndarray[np.uint32_t, ndim=1] starts = diploid.starts
    cdef np.ndarray[np.uint32_t, ndim=1] founder = diploid.founder
    cdef unsigned long end = diploid.end
    cdef unsigned long break_index, break_location
    cdef list non_duplicate = []
    break_indices = np.searchsorted(starts, locations)
    for break_location, break_index in zip(locations, break_indices):
        if break_location == end:
            continue
        if (break_index == starts.shape[0] or
            starts[break_index] != break_location):
            non_duplicate.append(break_location)
    cdef list return_starts = starts.tolist()
    return_starts.extend(non_duplicate)
    return_starts.sort()
    
    cdef list return_founder = []
    cdef unsigned long j = 0
    cdef unsigned long i = 0
    for i in range(len(return_starts)):
        if j < starts.shape[0] and return_starts[i] == starts[j]:
            return_founder.append(founder[j])
            j += 1
        else:
            return_founder.append(founder[j - 1])
    return Diploid(return_starts, diploid.end, return_founder)

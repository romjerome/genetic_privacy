"""# cython: profile=True"""
import numpy as np
from array import array

def common_segments_lengths(genome_a, genome_b):    
    common_founder_bits = np.unpackbits(genome_a._founder_bits & genome_b._founder_bits)
    common_founders = np.flatnonzero(common_founder_bits).tolist()
    common_segment_lengths = []
    a_map = genome_a._index_map
    b_map = genome_b._index_map
    a_mother = genome_a.mother
    a_father = genome_a.father
    b_mother = genome_b.mother
    b_father = genome_b.father
    for common_founder in common_founders:
        # "m" is mother, "f" is father
        a_starts_stops = get_founder_starts_stops(genome_a, common_founder,
                                                  a_map)
        a_m_starts, a_m_stops, a_f_starts, a_f_stops = a_starts_stops
        b_starts_stops = get_founder_starts_stops(genome_b, common_founder,
                                                  b_map)
        b_m_starts, b_m_stops, b_f_starts, b_f_stops = a_starts_stops
    return common_segment_lengths

cdef get_founder_starts_stops(genome, founder, index_map):
   """
   Given a genome and a founder, returns all the segments from that founder.
   """
   mother_starts = array("L", (genome.mother.starts[index]
                               for index in index_map.mother[founder]))
   mother_stops = array("L", (genome.mother.stops[index]
                              for index in index_map.mother[founder]))
   father_starts = array("L", (genome.father.starts[index]
                               for index in index_map.father[founder]))
   father_stops = array("L", (genome.father.stops[index]
                              for index in index_map.father[founder]))
   return (mother_starts, mother_stops, father_starts, father_stops)

cdef overlapping_regions(unsigned long[:] starts_a, unsigned long[:] stops_a,
                         unsigned long[:] starts_b, unsigned long[:] stops_b):
    cdef unsigned long len_a, len_b, index_a, index_b, start, stop
    cdef unsigned long a_start, a_stop, b_start, b_stop,
    len_a = len(starts_a)
    len_b = len(starts_b)
    index_a = 0
    index_b = 0
    shared_segments = []
    while index_a < len_a and index_b < len_b:
        a_start, a_stop = starts_a[index_a], stops_a[index_a]
        b_start, b_stop = starts_b[index_b], stops_b[index_b]

        # No region overlap in these cases, continue
        if a_stop < b_start:
            index_a += 1
            continue
        if b_stop < a_start:
            index_b += 1
            continue

        # Find out the overlap
        if a_start > b_start:
            start = a_start
        else:
            start = b_start
        if a_stop < b_stop:
            stop = a_stop
        else:
            stop = b_stop
        shared_segments.append((start, stop))
        
        if a_stop == b_stop:
            index_a += 1
            index_b += 1
        elif a_stop > b_stop:
            index_b += 1
        else:
            index_a += 1
    if len(shared_segments) <= 1:
        return shared_segments
    # consolidate contiguous segments eg if we have shared segments
    # (0, 5) and (5, 10), then we should merge them into (0, 10).
    # XXX: This now consolidates across chromosmoes, which may be undesirable
    return _consolidate_sequence(shared_segments)

cpdef common_homolog_segments(homolog_a, homolog_b):
    """
    Given two autosome homologs, returns a list of ranges (a, b), (b, c), ...
    where the two autosomes have the same underlying sequence.
    """
    cdef unsigned long len_a, len_b, index_a, index_b, start, stop
    cdef unsigned long a_start, a_stop, a_id, b_start, b_stop, b_id
    cdef unsigned long[:] starts_a = homolog_a.starts
    cdef unsigned long[:] stops_a = homolog_a.stops
    cdef unsigned long[:] founder_a = homolog_a.founder
    cdef unsigned long[:] starts_b = homolog_b.starts
    cdef unsigned long[:] stops_b = homolog_b.stops
    cdef unsigned long[:] founder_b = homolog_b.founder
    len_a = len(starts_a)
    len_b = len(starts_b)
    index_a = 0
    index_b = 0
    shared_segments = []
    while index_a < len_a and index_b < len_b:
        a_start, a_stop = starts_a[index_a], stops_a[index_a]
        a_id = founder_a[index_a]
        b_start, b_stop = starts_b[index_b], stops_b[index_b]
        b_id = founder_b[index_b]
        if a_id == b_id:
            if a_start > b_start:
                start = a_start
            else:
                start = b_start
            if a_stop < b_stop:
                stop = a_stop
            else:
                stop = b_stop
            shared_segments.append((start, stop))
        if a_stop == b_stop:
            index_a += 1
            index_b += 1
        elif a_stop > b_stop:
            index_b += 1
        else:
            index_a += 1
    if len(shared_segments) <= 1:
        return shared_segments
    # consolidate contiguous segments eg if we have shared segments
    # (0, 5) and (5, 10), then we should merge them into (0, 10).
    return _consolidate_sequence(shared_segments)

cdef _lengths(segments):
    """
    Takes a list of segments and returns a list of lengths.
    """
    cdef int a, b
    return [b - a for a, b in segments]

cpdef _consolidate_sequence(sequence):
    """
    Takes a list of elements of the form (a, b), (c, d), ...  and
    merges elements where b = c such that (a, b), (c, d) becomes (a, d)
    """
    cdef int i, j
    assert len(sequence) > 1
    i = 0
    j = 1
    consolidated = []
    while j < len(sequence):
        if sequence[j - 1][1] != sequence[j][0]:
            consolidated.append((sequence[i][0], sequence[j - 1][1]))
            i = j
        j += 1
    consolidated.append((sequence[i][0], sequence[j - 1][1]))
    return consolidated

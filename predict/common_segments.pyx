"""# cython: profile=True"""

def common_segment_lengths(genome_a, genome_b):
    """
    Given two genomes returns a list of integers for each autosome,
    corresponding to the length of segments that are shared between
    the two autosomes.
    """
    chromosomes_b = genome_b.chromosomes
    common_segment_lengths = dict()
    for name, autosome_a in genome_a.chromosomes.items():
        lengths = []
        autosome_b = chromosomes_b[name]
        lengths.extend(_lengths(common_homolog_segments(autosome_a.mother,
                                                        autosome_b.mother)))
        lengths.extend(_lengths(common_homolog_segments(autosome_a.father,
                                                        autosome_b.mother)))
        lengths.extend(_lengths(common_homolog_segments(autosome_a.mother,
                                                        autosome_b.father)))
        lengths.extend(_lengths(common_homolog_segments(autosome_a.father,
                                                        autosome_b.father)))
        common_segment_lengths[name] = lengths
    return common_segment_lengths

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

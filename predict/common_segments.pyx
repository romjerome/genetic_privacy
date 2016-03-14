
from recomb_genome import GENOME_ID_INDEX

def common_segment_lengths_cython(genome_a, genome_b):
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

def common_homolog_segments(homolog_a, homolog_b):
    """
    Given two autosome homologs, returns a list of ranges (a, b), (b, c), ...
    where the two autosomes have the same underlying sequence.
    """
    cdef int len_a, len_b, index_a, index_b, start, stop
    len_a = len(homolog_a)
    len_b = len(homolog_b)
    index_a = 0
    index_b = 0
    shared_segments = []
    while index_a < len_a and index_b < len_b:
        segment_a = homolog_a[index_a]
        segment_b = homolog_b[index_b]
        if segment_a[GENOME_ID_INDEX] == segment_b[GENOME_ID_INDEX]:
            start = max(segment_a[0], segment_b[0])
            stop = min(segment_a[1], segment_b[1])
            shared_segments.append((start, stop))
        if segment_a[1] == segment_b[1]:
            index_a += 1
            index_b += 1
        elif segment_a[1] > segment_b[1]:
            index_b += 1
        else:
            index_a += 1
    if len(shared_segments) <= 1:
        return shared_segments
    # consolidate contiguous segments eg if we have shared segments
    # (0, 5) and (5, 10), then we should merge them into (0, 10).
    return _consolidate_sequence(shared_segments)

def _lengths(segments):
    """
    Takes a list of segments and returns a list of lengths.
    """
    cdef int a, b
    return [b - a for a, b in segments]

def _consolidate_sequence(sequence):
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

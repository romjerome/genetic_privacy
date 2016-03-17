# cython: profile=True

cdef inline set _immediate_ancestors_of(nodes):
    """
    Given an iterable of nodes, returns set of nodes containing the
    parents of nodes in nodes.
    """
    ancestors = set()
    for node in nodes:
        if node is None:
            continue
        ancestors.add(node.mother)
        ancestors.add(node.father)
    ancestors.discard(None)
    return ancestors
    
def common_ancestor_vector(population, node_a, node_b):
    """
    Return a vector with where each entry is the length of a path from
    person_a to person_b through a common ancestor.
    """
    cdef int node_a_generation, node_b_generation, current_generation
    cdef int distance_to_a, distance_to_b
    if node_a == node_b:
        return (0,)
    node_to_generation = population.node_to_generation
    if node_to_generation[node_a] > node_to_generation[node_b]:
        temp = node_a
        node_a = node_b
        node_b = temp
    node_a_generation = node_to_generation[node_a]
    node_b_generation = node_to_generation[node_b]
    current_generation = node_b_generation
    ancestors_a = [node_a]
    ancestors_b = [node_b]
    while node_a_generation < current_generation:
        ancestors_b = _immediate_ancestors_of(ancestors_b)
        if node_a in ancestors_b:
            # One is a descandant of the other, therefore one of the
            # nodes is the only common ancestor which doesn't have a
            # path through a more recent common ancestor.
            return (node_b_generation - node_a_generation,)
        current_generation -= 1
    distances_vector = []
    assert node_a_generation == current_generation
    for current_generation in range(node_a_generation - 1, -1, -1):
        ancestors_a = _immediate_ancestors_of(ancestors_a)
        ancestors_b = _immediate_ancestors_of(ancestors_b)
        common_ancestors = ancestors_a.intersection(ancestors_b)
        distance_to_a = node_a_generation - current_generation
        distance_to_b = node_b_generation - current_generation
        new_distance = [distance_to_a + distance_to_b] * len(common_ancestors)
        distances_vector.extend(new_distance)
        # Don't look past the ancestors we have already counted.
        # eg it is more relevant that siblings share parents rather
        # than grandparents.
        ancestors_a.difference_update(common_ancestors)
        ancestors_b.difference_update(common_ancestors)
    distances_vector.sort() 
    return tuple(distances_vector)

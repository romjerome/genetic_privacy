"""# cython: profile=True"""

from collections import defaultdict, deque
from itertools import product

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

def precompute_vectors(population, labeled_nodes):
    relationship_vectors = defaultdict(list)
    for member in population.members:
        distances = _distances(member, labeled_nodes)
        for pair, distance in distances.items():
            relationship_vectors[pair].append(distance)
    for pair in relationship_vectors:
        relationship_vectors[pair].sort()
        relationship_vectors[pair] = tuple(relationship_vectors[pair])
    return defaultdict(tuple, relationship_vectors)

def _distances(ancestor, labeled_nodes):
    route = dict()
    distance_to_ancestor = dict()
    all_descendants = set()
    # We need to add ancestor to the list of descendants so that its
    # distance from its labeled children is recorded, and handle the
    # case it is itself labeled.
    distance_to_ancestor[ancestor] = 0
    route[ancestor] = None
    all_descendants.add(ancestor)
    for child in ancestor.children:
        route[child] = child
        distance_to_ancestor[child] = 1
        all_descendants.add(child)
    queue = deque(ancestor.children)
    while len(queue) > 0:
        node = queue.popleft()
        node_distance = distance_to_ancestor[node]

        for child in node.children:
            if child in all_descendants:
                continue
            distance_to_ancestor[child] = node_distance + 1
            route[child] = route[node]
            all_descendants.add(child)
        queue.extend(node.children)

    distance_to_labeled = dict()
    labeled_descendants = labeled_nodes.intersection(all_descendants)
    pairs = product(labeled_descendants,
                    (all_descendants - labeled_descendants))

    for labeled_node, descendant in pairs:
        if route[labeled_node] == route[descendant]:
           continue
        distance = distance_to_ancestor[descendant] + distance_to_ancestor[labeled_node]
        distance_to_labeled[(labeled_node, descendant)] = distance
    return distance_to_labeled
        

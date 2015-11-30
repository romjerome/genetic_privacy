from itertools import combinations
from random import sample

def proportion_within_distance(population, distance, percent_labeled):
    members = population.generations[-1].members
    num_labeled = int(percent_labeled * len(members))
    assert num_labeled > 0
    labeled = sample(members, num_labeled)
    ancestors = list()
    to_search = [(node, distance) for node in labeled]
    while len(to_search) > 0:
        current_node, current_distance = to_search.pop()
        assert current_node.mother is not None
        assert current_node.father is not None
        if current_distance == 1:
            ancestors.append(current_node.mother)
            ancestors.append(current_node.father)
            continue
        to_search.append((current_node.mother, distance - 1))
        to_search.append((current_node.father, distance - 1))
    assert len(to_search) is 0
    descendant_set = set()
    to_search.extend(ancestors)
    while len(to_search) > 0:
        current_node = to_search.pop()
        if current_node in descendant_set:
            continue
        descendant_set.add(current_node)
        to_search.extend(current_node.children)
    return len(descendant_set.intersection(members)) / len(members)
    

def length_shared(population):
    pass

def most_recent_common_ancestor(population):
    last_generation = population.generations[-1]
    for pair in combinations(last_generation.members):
        pass

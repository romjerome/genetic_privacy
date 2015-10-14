class IslandNode():
    def __init__(self, members, switch_probability, is_leaf = False):
        """
        Create a new island node with constituent members.  If is_leaf
        is true, then members will be individuals (Node objects from
        node.py that represent people).
        """
        self._parent = None
        self._is_leaf = is_leaf
        self._switch_probability = switch_probability
        # Don't use a generic "members" container, to potentially
        # catch mistakes where user think this node is a leaf when it
        # is not, or vice versa.
        if is_leaf:
            self._individuals = set(members)
        else:
            self._islands = frozenset(members)
            for node in members:
                node._parent = self

    def _add_indvidual(self, individual):
        self._individuals.add(individual)

    @property
    def is_leaf(self):
        return self._is_leaf

    @property
    def islands(self):
        return self._islands

    @property
    def individuals(self):
        return self._individuals

    @property
    def switch_probability(self):
        return self._switch_probability


class IslandTree():
    """
    Class to encapsulate switching probabilities in Hierarchical
    island tree model.
    """
    def __init__(self, root_node):
        self._root = root_node
        self._leaves = []
        self._individual_island = {}
        nodes = []
        nodes.append(root_node)
        while len(nodes.append) > 0:
            current_node = nodes.pop()
            if current_node.is_leaf:
                self._leaves.append(current_node)
                self._individual_island.update((individual, current_node)
                                               for individual
                                               in current_node.individuals)
            else:
                nodes.extend(current_node.islands)

    def get_island(self, individual):
        return self._indivdual_island[individual]

    def add_individual(self, island, individual):
        island._add_individual(individual)
        self._individual_island[individual] = island
                
    @property
    def root(self):
        return self._root

    @property
    def leaves(self):
        return self._leaves

    @property
    def individuals(self):
        return list(self._indivdual_island)
    


def tree_from_string(tree):
    # TODO: Implement this
    if isinstance(tree, str):
        tree = tree.split("\n")
    for line in tree:
        pass

def tree_from_file(f):
    with open(f, "r") as tree_file:
        return tree_from_string(tree_file.readlines())

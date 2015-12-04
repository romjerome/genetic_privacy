from random import choice

from sex import Sex, SEXES

class NodeGenerator:
    """
    We use a node generator so that nodes point to each other by id
    rather than by reference. This is purely a performance
    optimization that should allow pickle and other modules that use
    recursion to work on nodes and populations without overflowing the
    stack.
    """
    def __init__(self):
        self._id = 0
        self._mapping = dict()
        
    def generate_node(self, father = None, mother = None, sex = None):
        node_id = self._id
        self._id += 1
        if father is not None:
            father_id = father._id
        else:
            father_id = None
        if mother is not None:
            mother_id = mother._id
        else:
            mother_id = None
        node = Node(self, node_id, father_id, mother_id, sex)
        self._mapping[node_id] = node
        return node
    
    @property
    def mapping(self):
        return self._mapping

class Node:
    def __init__(self, node_generator, self_id, father_id = None,
                 mother_id = None, sex = None):
        self._node_generator = node_generator
        self._mother_id = mother_id
        self._father_id = father_id
        self._id = self_id
        if isinstance(sex, Sex):
            self.sex = sex
        else:
            self.sex = choice(SEXES)
        self._children = []
        if mother_id is not None:
            mother = self.mother
            assert mother.sex == Sex.Female
            mother._children.append(self._id)
        if father_id is not None:
            father = self.father
            assert father.sex == Sex.Male
            father._children.append(self._id)
        self.genome = None

    @property
    def mother(self):
        if self._mother_id is None:
            return None
        return self._node_generator.mapping[self._mother_id]

    @property
    def father(self):
        if self._father_id is None:
            return None
        return self._node_generator.mapping[self._father_id]

    @property
    def children(self):
        return [self._node_generator.mapping[node_id]
                for node_id in self._children]

    @property
    def node_generator(self):
        return self._node_generator

    # Define the rich comparison operator so that Nodes work in the
    # SymmetricDict. The ordering given by this is explicitly
    # different from the numbering used in _calculate_kinship.
    def __lt__(self, other):
        return self._id < other._id

    def __gt__(self, other):
        return self._id > other._id

from random import choice

from sex import Sex, SEXES

class Node:
    def __init__(self, father = None, mother = None, sex = None):
        self.mother = mother
        self.father = father
        if isinstance(sex, Sex):
            self.sex = sex
        else:
            self.sex = choice(SEXES)
        self.children = []
        if mother is not None:
            assert mother.sex == Sex.Female
            mother.children.append(self)
        if father is not None:
            assert father.sex == Sex.Male
            father.children.append(self)
        self.genome = None

    # Define the rich comparison operator so that Nodes work in the
    # SymmetricDict. The ordering given by this is explicitly
    # different from the numbering used in _calculate_kinship.
    def __lt__(self, other):
        return id(self) < id(other)

    def __gt__(self, other):
        return id(self) > id(other)

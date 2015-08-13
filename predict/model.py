
# From table F1 https://www.census.gov/hhes/families/data/cps2012F.html
# These numbers are not 100% accurate because each count is the count of
# children under 18.
CHILDREN_PROBABILITIES = {0: 45517/80506, 1: 15033/80506, 2: 12999/80506,
                          3: 4967/80506, 4:1990/80506}

class Node:
    def __init__(self, mom = None, dad = None, sex = None):
        self.mom = mom
        self.dad = dad
        self.sex = sex
        self.children = set()

class Generation:
    def __init__(self):
        pass
        

class Population:
    def __init__(self):
        self._generations = []

    def new_generation(self):
        """
        generates a new generation of individuals from the previous generation
        """
        pass

    

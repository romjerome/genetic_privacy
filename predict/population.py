from math import floor
from random import shuffle, uniform, choice
from itertools import chain, product, combinations_with_replacement
from types import GeneratorType
from pickle import Unpickler

from symmetric_dict import SymmetricDict
from generation import Generation

class Population:
    def __init__(self, initial_generation = None):
        self._generations = []
        self._kinship_coefficients = None
        self._node_to_generation = (None, -1)
        # The last n generations with genomes defined
        self._generations_with_genomes = None
        if initial_generation is not None:
            self._generations.append(initial_generation)

    @property
    def kinship_coefficients(self):
        if self._kinship_coefficients is None:
            self._kinship_coefficients = self._calculate_kinship()
        return self._kinship_coefficients

    @property
    def generations(self):
        return list(self._generations)

    @property
    def members(self):
        return chain.from_iterable(generation.members for
                                   generation in self._generations)

    @property
    def size(self):
        return sum(generation.size for generation in self._generations)

    @property
    def node_to_generation(self):
        """
        Maps nodes in this population to their generation.
        Higher numbered generations are more recent.
        """
        # Cache the results of this function so it only needs to be
        # computed when new generations are added.
        cached = self._node_to_generation
        if cached[0] is not None and cached[1] == len(self._generations):
            return cached[0]        
        generations = [generation.members for generation in self._generations]
        node_to_generation = dict()
        for generation_num, members in enumerate(generations):
            for node in members:
                node_to_generation[node] = generation_num
        self._node_to_generation = (node_to_generation, len(self._generations))
        return node_to_generation

    def clean_genomes(self, generations = None):
        """
        Remove genomes from the first n given number of generations.
        If generations is not specified, clears all generations genomes.
        """
        if generations is None:
            generations = self.num_generations
        # We want to start with the nodes that have genomes defined.
        if self._generations_with_genomes is None:
            start = 0
        else:
            start = self.num_generations - self._generations_with_genomes
        generations_to_clear = self._generations[start:generations]
        for person in chain.from_iterable(generation.members for generation
                                          in generations_to_clear):
            del person.genome


    @property
    def num_generations(self):
        """
        Return the number of generations
        """
        return len(self._generations)

    def new_generation(self, size = None):
        """
        Generates a new generation of individuals from the previous
        generation.  If size is not passed, the new generation will be
        the same size as the previous generation.
        """
        if size is None:
            size = self._generations[-1].size
        previous_generation = self._generations[-1]
        new_nodes = []
        men = list(previous_generation.men)
        shuffle(men)
        women = list(previous_generation.women)
        pairs = []
        for man in men:
            if len(women) is 0:
                break
            # We go backwards through the list of women, so we pop
            # them off the end of the list.
            for i in range(len(women) - 1, -1, -1):
                if man.mother is None or women[i].mother != man.mother:
                    pairs.append((man, women.pop(i)))
                    break
        min_children = floor(size / len(pairs))
        # Number of families with 1 more than the min number of
        # children. Because only having 2 children per pair only works
        # if there is an exact 1:1 ratio of men to women.
        extra_child = size - min_children * len(pairs)
        for i, (man, woman) in enumerate(pairs):
            if i < extra_child:
                extra = 1
            else:
                extra = 0
            for i in range(min_children + extra):
                child = man.node_generator.generate_node(man, woman)
                new_nodes.append(child)

        SIZE_ERROR = "Generation generated is not correct size. Expected {}, got {}."
        assert len(new_nodes) == size, SIZE_ERROR.format(size, len(new_nodes))
        self._generations.append(Generation(new_nodes))

    def _symmetric_members(self):
        """
        Generator that yields 2 item tuples that contain members of
        the popluation. Generates all pairs of members, where members
        are visited in the first entry of the tuple first.
        TODO: Can this be replaced by itertools.combinations_with_replacement?
        """
        members = list(self.members)
        return ((members[y], members[x])
                for x in range(len(members))
                for y in range(x, len(members)))

    def _clean_kinship(self, kinship,  generation):
        """
        Remove entries from the kinship dictionary for members of
        the given generation.
        """
        # Delete within the generation as a special case to avoid
        # (x,y) (y, x) repeats you get with products.
        current_members = self._generations[generation].members
        for p_1, p_2 in combinations_with_replacement(current_members, 2):
            del kinship[p_1, p_2]
        later_gen = chain.from_iterable(gen.members for gen
                                        in self._generations[generation + 1:])
        for p_1, p_2 in product(current_members, later_gen):
            del kinship[p_1, p_2]

    def _calculate_kinship(self, only_keep = 3):
        # Calculated based on
        # http://www.stat.nus.edu.sg/~stachenz/ST5217Notes4.pdf
        kinship = SymmetricDict()
        # We need to be sure we recursively look up kinship coeff on
        # the higher numbered person, as given in the pdf. Therefore
        # we need a number for each person.
        generation_dict = {member: i for i, generation
                           in enumerate(self.generations)
                           for member in generation.members}
        last_cleaned = -1
        for person_1, person_2 in self._symmetric_members():
            key = (person_1, person_2)
            if person_1 is person_2:
                if person_1.mother is None:
                    kinship[key] = 0.5
                    continue
                parents = (person_1.mother, person_1.father)
                coeff = 0.5 + (0.5) * kinship[parents]
                kinship[key] = coeff

                # This conditional needs to be here because we can
                # only start on a new generation when person_2 is
                # incremented, which first happens when
                # person_1 == person_2
                generation = generation_dict[person_2]
                if generation - only_keep > last_cleaned:
                    self._clean_kinship(kinship, last_cleaned + 1)
                    last_cleaned += 1
                continue
            
            if person_1.mother is None:
                kinship[key] = 0
                continue
            
            coeff_1 = kinship[(person_1.mother, person_2)]
            coeff_2 = kinship[(person_1.father, person_2)]
            kinship[key] = 0.5 * (coeff_1 + coeff_2)
        return kinship

class HierarchicalIslandPopulation(Population):
    """
    A population where mates are selected based on
    locality. Individuals exists on "islands", and will search for
    mates from a different island with a given switching probability.
    """
    def __init__(self, island_tree, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._island_tree = island_tree
        # Assume existing members of the tree are a part of the founders
        if len(island_tree.individuals) > 0:
            assert len(self._generations) is 0
            self._generations.append(Generation(island_tree.individuals))


    def _pick_island(self, individual):
        island = self._island_tree.get_island(individual)
        # Traverse upward
        while uniform(0, 1) < island.switch_probability:
            island = island.parent
            if island.parent is None:
                break
        # Now drill down into final island.
        while not island.is_leaf:
            island = choice(list(island.islands))
        return island

    def _island_members(self, generation_members):
        """
        Returns a dictionary mapping islands to sets of individuals
        from generation_members.
        """
        if isinstance(generation_members, GeneratorType):
            # If generation_members is a generator, then all the
            # elements are "used up" on the first leaf. We need to
            # iterate over the elements of generation_members multiple
            # time.
            generation_members = list(generation_members)
        members = dict()
        for leaf in self._island_tree.leaves:
            m = list(leaf.individuals.intersection(generation_members))
            members[leaf] = m
            shuffle(m)
        return members
            

    def new_generation(self, size = None):
        """
        Generates a new generation of individuals from the previous
        generation. If size is not passed, the new generation will be
        the same size as the previous generation.
        """
        if size is None:
            size = self._generations[-1].size
        previous_generation = self._generations[-1]
        men = list(previous_generation.men)
        shuffle(men)
        available_women = self._island_members(previous_generation.women)
        pairs = []
        for man in men:
            if sum(len(members) for members in available_women.values()) is 0:
                break
            island = self._pick_island(man)
            island_women = available_women[island]
            if len(island_women) is 0:
                # There are no mates on this island for this man This
                # man will go unpaired, which shouldn't cause too many
                # issues in large populations.
                continue
            for i in range(len(island_women) - 1, -1 , -1):
                if man.mother is None or island_women[i].mother != man.mother:
                    pairs.append((man, island_women.pop(i)))
                    break
        min_children = floor(size / len(pairs))
        # Number of families with 1 more than the min number of
        # children. Because only having 2 children per pair only works
        # if there is an exact 1:1 ratio of men to women.
        extra_child = size - min_children * len(pairs)
        node_generator = men[0].node_generator
        new_nodes = []
        for i, (man, woman) in enumerate(pairs):
            if i < extra_child:
                extra = 1
            else:
                extra = 0
                
            # Child will be based at mother's island
            island = self.island_tree.get_island(woman)
            for i in range(min_children + extra):
                child = node_generator.generate_node(man, woman)
                new_nodes.append(child)
                self.island_tree.add_individual(island, child)
                
        SIZE_ERROR = "Generation generated is not correct size. Expected {}, got {}."
        assert len(new_nodes) == size, SIZE_ERROR.format(size, len(new_nodes))
        self._generations.append(Generation(new_nodes))

    @property
    def island_tree(self):
        return self._island_tree

class PopulationUnpickler(Unpickler):
    def load(self):
        result = super().load()
        for member in result.members:
            member._resolve_parents()
        return result

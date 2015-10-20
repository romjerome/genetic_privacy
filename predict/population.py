from math import floor
from random import shuffle, uniform, choice
from collections import deque
from itertools import chain, product, combinations_with_replacement

from symmetric_dict import SymmetricDict
from genome import GenomeGenerator
from node import Node
from generation import Generation

class Population:
    def __init__(self, initial_generation = None):
        self._generations = []
        self._kinship_coefficients = None
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

    def generate_genomes(self):
        generator = GenomeGenerator()
        # I don't use recursion because python doesn't do well with
        # deep recursion
        queue = deque(self._generations[0].members)
        while len(queue) > 0:
            person = queue.popleft()
            if person.genome is not None:
                continue
            # An optimization would be to only add children if person is female
            # This way people only go into the queue once.
            queue.extend(person.children)
            mother = person.mother
            father = person.father
            if mother is None:
                person.genome = generator.generate_genome()
                continue
            person.genome = mother.genome.mate(father.genome)
            
            

    def clean_genomes(self, generations = None):
        """
        Remove genomes from the first n given number of generations.
        If generations is not specified, clears all but the last
        generations genomes.
        """
        if generations is None:
            generations = self.num_generations - 1
        for person in chain.from_iterable(generation.members for generation
                                          in self._generations[:generations]):
            person.genome = None


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
                new_nodes.append(Node(man, woman))

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
        members = dict()
        for leaf in self._island_tree.leaves:
            members[leaf] = leaf.individuals.intersection(generation_members)
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
        new_nodes = []
        men = list(previous_generation.men)
        shuffle(men)
        available_women = self._island_members(previous_generation.women)
        pairs = []
        for man in men:
            if sum(len(members) for members in available_women.values()) is 0:
                break
            island = self._pick_island(man)
            island_women = list(available_women[island]) 
            if len(island_women) is 0:
                # There are no mates on this island for this man This
                # man will go unpaired, which shouldn't cause too many
                # issues in large populations.
                continue
            mate = choice(island_women)
            if mate.mother is not None or mate.mother is man.mother:
                # We don't build this for every man because it isn't
                # efficient. Chances are if we pick randomly, we will
                # get an appropriate mate.
                island_women = filter((lambda m: m.mother is None or
                                       m.mother is not man.mother),
                                      available_women[island])
                island_women = list(island_women)
                if len(island_women) is 0:
                    continue
                mate = choice(island_women)
            pairs.append((man, mate))
            available_women[island].remove(mate)
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
                
            # Child will be based at mother's island
            island = self.island_tree.get_island(woman)
            for i in range(min_children + extra):
                child = Node(man, woman)
                new_nodes.append(child)
                self.island_tree.add_individual(island, child)
                
        SIZE_ERROR = "Generation generated is not correct size. Expected {}, got {}."
        assert len(new_nodes) == size, SIZE_ERROR.format(size, len(new_nodes))
        self._generations.append(Generation(new_nodes))

    @property
    def island_tree(self):
        return self._island_tree

from random import choice
from os import getpid
from uuid import uuid4
from weakref import ref
import shelve

from sex import Sex, SEXES

class NodeGenerator:
    """
    We use a node generator so that nodes point to each other by id
    rather than by reference. Pickle does not handle highly recursive
    datastructures well. This is a performance optimization that
    should allow pickle and other modules that use recursion to work
    on nodes and populations without overflowing the stack.  The IDs
    are also usefull when using multiprocessing, as just the Node's id
    can be passed from one process to the other.
    """
    def __init__(self, genome_file = None):
        self._id = 0
        self._mapping = dict()
        self.genome_manager = GenomeManager(genome_file)
        
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

class GenomeManager:
    """
    Genomes for large popualtions start to take a large amount of RAM,
    so genomes must be stored on disk.
    GenomeManager manages the state for nodes genomes, serializing the
    genomes to disk. Part of GenomeManager's job is managing
    persistence across multiple processes.
    """
    def __init__(self, filename = None):
        if filename is None:
            filename = "genome_db_" + str(uuid4()) + ".shelve"
        self._filename = filename
        self._setup_db()

    def reorganize(self):
        """
        Call "reorganize" on underlying database.
        Useful when a lot of elements have been deleted from the database.
        """
        self._db.sync()
        self._db.dict.reorganize()

    def _setup_db(self):
        self._db_pid = getpid()
        self._db = shelve.open(self._filename, flag = "cuf",
                               protocol = 4)        

    def __getitem__(self, key):
        if self._db_pid != getpid():
            # This object was not created in this process, we need a
            # fresh connection to the db, because shelve objects
            # created in parent processes do not work in child
            # processes.
            self._setup_db()
        return self._db[key]

    def __setitem__(self, key, value):
        if self._db_pid != getpid():
            self._setup_db()
        self._db[key] = value

    def __contains__(self, item):
        if self._db_pid != getpid():
            self._setup_db()
        return item in self._db

    def __delitem__(self, key):
        if self._db_pid != getpid():
            self._setup_db()
        del self._db[key]

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_db_pid"]
        del state["_db"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._setup_db()

class Node:
    def __init__(self, node_generator, self_id, father_id = None,
                 mother_id = None, sex = None):
        self._node_generator = node_generator
        self._genome_manager = node_generator.genome_manager
        self._mother_id = mother_id
        self._father_id = father_id
        self._id = self_id
        self._str_id = str(self_id)
        self._genome = lambda: None # Weakref of genome
        if isinstance(sex, Sex):
            self.sex = sex
        else:
            self.sex = choice(SEXES)
        self._children = []
        self._resolve_parents()
        if self.mother is not None:
            assert self.mother.sex == Sex.Female
            self.mother._children.append(self._id)
        if self.father is not None:
            assert self.father.sex == Sex.Male
            self.father._children.append(self._id)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["mother"]
        del state["father"]
        del state["_genome"]
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._genome = lambda: None
        # Parents are resolved by PopulationUnpickler after all Node
        # objects are created

    def _resolve_parents(self):
        if self._mother_id is not None:
            self.mother = self._node_generator._mapping[self._mother_id]
        else:
            self.mother = None
        if self._father_id is not None:
            self.father = self._node_generator._mapping[self._father_id]
        else:
            self.father = None

    @property
    def genome(self):
        maybe_genome = self._genome()
        if maybe_genome:
            return maybe_genome
        if self._str_id in self._genome_manager:
            return self._genome_manager[self._str_id]
        return None

    @genome.setter
    def genome(self, value):
        self._genome = ref(value)
        self._genome_manager[self._str_id] = value

    @genome.deleter
    def genome(self):
        self._genome = lambda: None
        del self._genome_manager[self._str_id]
            
    @property
    def mapping(self):
        return self._node_generator._mapping

    @property
    def children(self):
        return [self._node_generator._mapping[node_id]
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

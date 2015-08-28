import pdb
from simuPOP import *

pop = Population(size=10000, loci=[1000], ancGen = -1,
                 infoFields=['ind_id', 'father_id', 'mother_id'])
pop.evolve(
    initOps = [InitSex(),
               IdTagger(),
               PedigreeTagger()],
    matingScheme = MonogamousMating(ops = [Recombinator(rates=0.01),
                                           IdTagger(),
                                           PedigreeTagger()]),
    gen = 10)

ped = Pedigree(pop)
print(pop.ancestralGens())
print(len(list(pop.individuals())))
test_individual = pop.individual(9000)
print(test_individual.info("ind_id"))
print(ped.identifyAncestors(test_individual.info("ind_id")))
print(len(ped.identifyAncestors(test_individual.info("ind_id"))))


pdb.set_trace()

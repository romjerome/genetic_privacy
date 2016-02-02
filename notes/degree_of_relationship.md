https://en.wikipedia.org/wiki/Coefficient_of_relationship#Human_relationships

n-th cousin doesn't work well because it doesn't map onto every
pairwise relationship cleanly, ie as a single number.

Degree of relationship isn't great either, as pair who share
significantly more genes may be assigned the same degree of
relationship as pairs who share less. For example full siblings and
half sibling have the same degree of relationship even though they
share 50% and 25% of their genes, respectively.

We could try bucketing based on kinship coefficient.

Idea:

Use relationship (eg full siblings, double first cousins) and learn the distributions of those. This relationship can be represented by a vector rather than by human readable words. The vectors would be made up of the paths between the two individuals, where the entry is the length of the shortest path length. Not all possible vectors will map onto realistic relationships.

Thoughts on the qualitative differences between relations who may have the same kinship coefficient:

http://familypedia.wikia.com/wiki/Double_first_cousin

>  While double first cousins have the same coefficient of coancestry (1/8) as half-siblings, they do have higher chances of sharing BOTH alleles (1/16 vs 0) and lower chances of sharing one allele (3/8 vs 1/2) with each other than half-siblings.

ie double first cousins have the same % dna shared, but certain combinations are possible in double first cousins that are not possible in half-siblings.


Types of recombination
----------------------
There are two types of recombination, cross over recombination (CO)
and non cross over recombination (NCO).  Non cross over recombination
doesn't seem to have an effect linkage disequlibrium.  Cross over
recombination happens most often between homologous chromosomes.  NCO
seems to be more common the cross over recombination.  See:
http://cdn.intechopen.com/pdfs-wm/23159.pdf page 7

Is this reflected in the hapmap data?

Recombination may vary person to person, not just by sex:
http://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1000831

According to
http://hapmap.ncbi.nlm.nih.gov/downloads/recombination/2005-06_16a_phaseI/00README.txt
the hapmap data analysis was performed using LDhat. Manual here:
http://ldhat.sourceforge.net/manual.pdf

Questions
---------

When there is a recombination hotstop, does that mean there is a lot
of recombination happening within that region, or that recombination
is often initiated inside that region and continues outside of it? Are
recombination locations independent?

Assumptions I make in modeling recombination
--------------------------------------------

Although there may be differences in where recombination happens in
men vs women, I will assume that the recombination rates in women and
men are multipliers on top of some "yard stick" recombination rate. I
use the HapMap recombination rates as the yard stick, and the decode
data set to determine the multipliers.

12-22-15
========
* Disambiguate degree of relationship vs nth cousin
* Don't use naive bayes to determine relatedness at first. Instead use total length of shared segments. Only use bayes later if it gives better results.
* Use naive bayes / likelikhood maximizaion on vector of relatedness to determine the individual.

03-01-16
========

* See if it is possible to determine distribution automatically.
* Sanity check the distributions against other results or data.
* See if it is possible to do on demand determination of distributions.
* Try to understand if the different types of relationships that share a vector have different distributions. eg for (2, 2) is the distribution of siblings vs siblings who have had a kid with eachother (compared to the grandparent) the same?


Command to generate section headers:
date +"%m-%d-%y"

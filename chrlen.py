chromelengths = [None, 247249719, 242951149, 199501827, 191273063, 180857866, 170899992, 158821424, 146274826, 140273252, 135374737, 134452384, 132349534, 114142980, 106368585, 100338915, 88827254, 78774742, 76117153, 63811651, 62435964, 46944323, 49691432]

#chromelengths = dict((i, chrlen[i-1]) for i in xrange(1,23)) #only autosomes,

#sniplengths = dict((i, chromelengths[i]/2800) for i in xrange(1, 23))

sniplengths = [x/2800 if x else None for x in chromelengths]

geneticlengths = [None, 274.27, 259.43, 221.83, 204.47, 205.69, 189.6, 182.96, 166.08, 160.01, 177.19, 152.45, 171.96, 129.52, 122.82, 133.61, 129.99, 137.99, 121.65, 109.73, 98.63, 65.59, 68.82, 188.22]
geneticlengths = [x/100 if x else None for x in geneticlengths]

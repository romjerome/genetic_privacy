import pylab

for chr in xrange(1,24):
    pylab.scatter([float(l[-1]) for l in lines if int(l[0]) == chr], [float(l[-2]) for l in lines if int(l[0]) == chr])
    time.sleep(2)
    pylab.close()

lines = open(data_dir + 'recombination-map.csv') | pTail(skip=30) | pGrep('NA', invert=True) | pSplit(',')

chr1 = [utils.Struct(pos=int(l[3]), gd=float(l[4]), rr=float(l[7])) for l in lines if l[0] == '1']

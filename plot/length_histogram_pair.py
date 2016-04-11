import sqlite3
from random import choice

import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import beta

LENGTH_DB = "/media/paul/Storage Monster/scratch/lengths.db"
conn = sqlite3.connect(LENGTH_DB)

c = conn.cursor()

query = c.execute("""SELECT DISTINCT unlabeled, labeled from lengths
                     WHERE shared > 100""")
nonzero_pairs = [(unlabeled, labeled) for unlabeled, labeled in query]

def get_lengths(unlabeled, labeled, cur):
    q = cur.execute("""SELECT shared from lengths
                       WHERE unlabeled = ? AND labeled = ?""", (unlabeled,
                                                                labeled))
    lengths = [length[0] for length in q]
    return np.array(lengths)
    
def plot_histogram(lengths):
    lengths.sort()
    plt.hist(lengths, bins = 20, normed = True)
    # plt.hist(lengths, bins = 20)
    pdf = beta(*beta.fit(lengths)).pdf(lengths)
    plt.plot(lengths, pdf)
    plt.show()


lengths = get_lengths(9434, 8621, c)
plot_histogram(lengths)
for unlabeled, labeled in nonzero_pairs:
    lengths = get_lengths(unlabeled, labeled, c)
    if np.var(lengths) < 100:
        continue
    import pdb
    pdb.set_trace()
    plot_histogram(lengths)
    
conn.close()

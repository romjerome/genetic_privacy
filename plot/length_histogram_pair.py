import sqlite3
from random import choice

import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import beta, gamma, poisson

LENGTH_DB = "/media/paul/Storage/scratch/lengths_1000.db"
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
    plt.hist(lengths, bins = 30, normed = True)
    # plt.hist(lengths, bins = 20)
    np_lengths = np.array(lengths)
    beta_pdf = beta(*beta.fit(np_lengths)).pdf(np_lengths)
    gamma_pdf = gamma(*gamma.fit(np_lengths)).pdf(np_lengths)

    
    beta_plot = plt.plot(lengths, beta_pdf, label = "Beta")
    gamma_plot = plt.plot(lengths, gamma_pdf, label = "Gamma")
    plt.legend(loc = "upper right")
    plt.show()


for unlabeled, labeled in nonzero_pairs:
    lengths = get_lengths(unlabeled, labeled, c)
    if np.var(lengths) < 100:
        continue
    import pdb
    # pdb.set_trace()
    plot_histogram(lengths)
    
conn.close()

from random import choice
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import beta, gamma, poisson, exponweib

LENGTHS_FILENAME = "lengths/70004"

def get_lengths(lengths_filename):
    lengths = defaultdict(list)
    with open(lengths_filename, "r") as lengths_file:
        for line in lengths_file:
            try:
                node_id, length = line.split("\t")
            except ValueError:
                continue
            node_id = int(node_id)
            length = int(length)
            if node_id > 100000 or length > 10000000000:
                continue
            lengths[node_id].append(length)
    return lengths
            
    
def plot_histogram(lengths):
    lengths.sort()
    weights = np.ones_like(lengths)/float(len(lengths))
    plt.hist(lengths, weights=weights, bins = 20)

    np_lengths = np.array(lengths)
    beta_pdf = beta(*beta.fit(np_lengths)).pdf(np_lengths)
    gamma_pdf = gamma(*gamma.fit(np_lengths)).pdf(np_lengths)
    exponweib_pdf = exponweib(*exponweib.fit(np_lengths)).pdf(np_lengths)

    beta_plot = plt.plot(lengths, beta_pdf, label = "Beta")
    gamma_plot = plt.plot(lengths, gamma_pdf, label = "Gamma")
    weib_plot = plt.plot(lengths, exponweib_pdf, label = "Exp Weib")
    plt.legend(loc = "upper right")
    plt.show()

lengths_vectors = get_lengths(LENGTHS_FILENAME)
for node_id, lengths in lengths_vectors.items():
    plot_histogram(lengths)

for unlabeled, labeled in nonzero_pairs:
    lengths = get_lengths(unlabeled, labeled, c)
    if np.var(lengths) < 100:
        continue
    import pdb
    # pdb.set_trace()
    plot_histogram(lengths)
    
conn.close()

#!/usr/bin/env python3

from pickle import load
from math import floor, ceil, sqrt
from scipy.stats import gamma

import numpy as np
import matplotlib.pyplot as plt

LENGTH_CUTOFF = 25000
DIST_NAMES = ['gamma', 'norm']

with open("lengths_file.pickle", "rb") as lengths_file:
    lengths = load(lengths_file)

plot_count = len(list(filter(lambda x: LENGTH_CUTOFF < len(x),
                             lengths.values())))
num_col = int(floor(sqrt(plot_count)))
num_row = int(ceil(plot_count / num_col))

sorted_relationships = sorted(lengths.keys(), key = sum)

plt.figure(1)
subplot_num = 1
for relationship in sorted_relationships:
    length_data = lengths[relationship]
    length_data.sort()
    if LENGTH_CUTOFF > len(length_data):
        continue
    plt.subplot(num_row, num_col, subplot_num)
    plt.hist(length_data, bins = 200, normed = True)
    plt.title(str(relationship))

    fit = gamma.fit(length_data)
    pdf = gamma(*fit).pdf(length_data)
    plt.plot(length_data, pdf)
    subplot_num += 1

plt.tight_layout()
plt.show()
    

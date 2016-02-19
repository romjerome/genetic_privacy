#!/usr/bin/env python3

from pickle import load
from math import floor, ceil, sqrt

import numpy as np
import matplotlib.pyplot as plt

LENGTH_CUTOFF = 30000

with open("lengths_file.pickle", "rb") as lengths_file:
    lengths = load(lengths_file)

plot_count = len(list(filter(lambda x: LENGTH_CUTOFF < len(x),
                             lengths.values())))
num_col = int(floor(sqrt(plot_count)))
num_row = int(ceil(plot_count / num_col))

plt.figure(1)
subplot_num = 1
for relationship, length_data in lengths.items():
    if LENGTH_CUTOFF > len(length_data):
        continue
    plt.subplot(num_row, num_col, subplot_num)
    plt.hist(length_data)
    plt.title(str(relationship))
    subplot_num += 1

plt.show()
    


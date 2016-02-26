import matplotlib.pyplot as plt
from scipy.stats import truncnorm, gamma
import numpy as np
from pickle import load

with open("lengths_file.pickle", "rb") as lengths_file:
    lengths = load(lengths_file)


data = [10334157, 49243020, 8054510, 74055442, 29628988, 0, 95662961,
25858267, 46418312, 94619500, 71168308, 73255226, 15952414, 29958148,
94730820, 37106761, 52380769, 46388154, 61749611, 11186680, 97246803,
12328650, 68025049, 34618585, 53514443, 20820149, 2672224, 40524828,
23936826, 10070882, 24241012, 9419606, 46726522, 50629147, 0,
25578951, 79531409, 142564739, 23745932, 8174951, 73594472, 48660713,
51649161, 35863046, 74586030, 86042964, 6255463, 0, 102355256,
15950132, 41718018, 16270646, 5167288, 33860558, 17430532, 33419416,
13591085, 39543273, 35889878, 64348941, 99169626, 65208071, 54695282,
22208123, 34313072, 60476810, 34265015, 107700576, 39040086, 14370686,
74420931, 65461655, 8907874, 80441712, 65971271, 20543220, 59147738,
23304334, 130258928, 18452922, 42620009, 77351045, 76032324, 44196273,
49036974, 23245119, 50656670, 84837088, 2089074, 52517589, 21469409,
106694589, 67063796, 16053222, 101270899, 15620252, 18355964, 839197,
31083111, 66698677]

# mean = np.mean(data)
# var = np.var(data)
# fit = truncnorm.fit(data, 0, 2866387308, loc = mean, scale = var)
# print(fit)
# print(truncnorm(*fit).rvs(100))
# vector = lengths[(2, 2)]
vector = np.array(sorted(lengths[(5, 5)]))

mean = np.mean(vector)
var = np.var(vector)
std = np.std(vector)
# fit = truncnorm.fit(vector, a = 0, b = 2866387308, loc = mean, scale = var)
fit = gamma.fit(vector)
print(fit)
# pdf = gamma.pdf(vector, *fit[:-2], loc = fit[-2], scale = fit[-1])
pdf = gamma(*fit).pdf(vector)
print(pdf)
# print(gamma.pdf(vector, alpha))

plt.figure()
plt.hist(vector, bins = 20, normed = True)
# plt.hist(truncnorm(*fit).rvs(10000), bins = 20, normed = True, alpha = 0.5)
plt.plot(vector, pdf)
# plt.hist(gamma(*fit).rvs(10000), bins = 20, normed = True, alpha = 0.5)
plt.show()

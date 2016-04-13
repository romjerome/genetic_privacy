from math import log # Python's built in log is faster for non vector operations

import numpy as np
from scipy.special import digamma, polygamma


def fit_gamma(data):
    """
    Gamma parameter estimation using the algorithm described in
    http://research.microsoft.com/en-us/um/people/minka/papers/minka-gamma.pdf
    Returns a tuple with (shape, scale) parameters.
    """
    log_of_mean = log(np.mean(data))
    mean_of_logs = np.mean(np.log(data))
    log_diff = mean_of_logs - log_of_mean
    a = 0.5 / (log_of_mean - mean_of_logs)
    a_reciprocal = 1/a
    difference = 1
    while difference > 0.000005:
        numerator = log_diff + log(a) - digamma(a)
        denominator = (a ** 2) * (a_reciprocal - polygamma(1, a))
        tmp_a_reciprocal = a_reciprocal + numerator / denominator
        tmp_a = 1 / tmp_a_reciprocal
        difference = abs(tmp_a - a)
        a = tmp_a
        a_reciprocal = tmp_a_reciprocal
    return (a, np.mean(data) / a)

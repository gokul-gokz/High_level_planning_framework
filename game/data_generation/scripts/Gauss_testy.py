"""
This script is used for GENERATING and COMPARING gaussian representations of data.  It is a work in progress.
So far, it can compute the Covariance Matrix and Mean Vector for a given set of data.

compute_bhattacharyya(...) is based on https://en.wikipedia.org/wiki/Bhattacharyya_distance, and is ideally
meant to be used as a generic Gaussian Comparator.  That said, it does not yet seem to be working with the
9-dimensional multivariate Gaussians that our data fits to.

Gunnar Horve <gunnarhorve@gmail.com>
Last Update: 04/30/2018
"""

import pickle
import definitions as d
import numpy as np

def compute_bhattacharyya(mu1, mu2, sig1, sig2):
    sig = (sig1 + sig2)/2

    log_den = abs(np.linalg.det(sig1) * np.linalg.det(sig2))
    log_num = abs(np.linalg.det(sig))

    dist = 1/8 * np.transpose(mu1 - mu2) * np.linalg.inv(sig) * (mu1 - mu2) + \
        1/2 * np.log(log_num/log_den)

    return dist

raw_data = pickle.load(open(d.TRAINING_DATA, "rb"))

#  computes the mean and covariance for set_1
effect_data_1 = np.array([s_r_s[3] for s_r_s in raw_data[0:2000]])
effect_data_1 = np.swapaxes(effect_data_1, 0, 1)

#  computes the mean and covariance for set_2
effect_data_2 = np.array([s_r_s[3] for s_r_s in raw_data[2000:4000]])
effect_data_2 = np.swapaxes(effect_data_2, 0, 1)


# be sad when the thing doesn't work
ans = compute_bhattacharyya(np.mean(effect_data_1, axis=1),  np.mean(effect_data_2, axis=1),
                            np.cov(effect_data_1), np.cov(effect_data_2))

print "7"  # this line for breakpoint placement

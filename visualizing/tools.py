from math import sqrt, sin, cos, acos, asin, pi
import numpy as np
import pickle

def spherical(p1, p2):
    x_dis = float(p2[0] - p1[0])
    y_dis = float(p2[1] - p1[1])
    dis = sqrt(x_dis ** 2 + y_dis ** 2)

    return dis

def gaussian_r(samples):
    if len(samples[0]) >= 2:
        avg = np.average(samples, axis=0)
        center = avg[0:2]
        dists = []
        for i in samples:
            dists.append(spherical(center, i))

    else:
        avg = np.average(samples)
        dists = []
        for i in samples:
            dists.append(np.abs(avg-i))

    dists.sort()
    return dists[int(len(dists)*0.95)]


if __name__ == '__main__':
    f = open('temp_output.p')
    (P, P_masks) = pickle.load(f)
    f.close()

    samples = P['p10'].sample(100)
    gaussian_r(samples)
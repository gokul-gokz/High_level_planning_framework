"""
This script contains the main logic of the data clustering required for PPDDL generation,
per section 4.3.1 LEARNING A SYMBOLIC REPRESENTATION FROM EXPERIENCE of http://irl.cs.brown.edu/pubs/orig_sym_jair.pdf.

Common Variable Definitions:
    s/old:      a single effect state prior to completing an option (9-dimensional tuple)
    o:          an option                                           (string)
    r:          the reward associated with completing an option     (integer)
    s'/new:     a single effect state resulting from an option      (9-dimensional tuple)


Basically for a given data set (records.p), for a given set of options, it calls:
    partition_masks(...)
    create_effect_partitions(...)
    merge_partitions(...)

The bottommost section, dedicated to the generation of groundings, is not currently functional

Gunnar Horve <gunnarhorve@gmail.com>
Last Update: 04/30/2018
"""

import pickle
import math
import numpy as np                  # left in case helpers.py import is ever removed
from itertools import compress
from os.path import dirname, abspath
#import definitions as d
from helpers import *
from mat2csv import *

# ------------------------v Partitioning Steps v------------------------ #
def partition_masks(option_training_data):
    """
    given the raw training data for a given option, partition based on mask
    :param option_training_data: list of data matching [(s, o, r, s'), (s, o, r, s'), ...]
    :return: a dictionary mapping mask to a corresponding subset of the input {[bool]: [(s,o,r,s'), (s,o,r,s'), ...]}
    """

    partitions = {}       # maps mask (as int) to set of records
    for old, o, r, new in option_training_data:

        mask = tuple([abs(old[idx] - new[idx]) >= 15 for idx in range(len(old))])

        if mask not in partitions.keys():
            partitions[mask] = []

        partitions[mask].append((old, r, new))
    return partitions

def create_effect_partitions(mask_partitions):
    """
    given the mask partitions for an option, partitions data based on effects (s')
    :param mask_partitions: a dictionary mapping masks to raw training data {[bool]: [(s,o,r,s'), (s,o,r,s'), ...]}
    :return: data partitioned by mask AND effect: effect_partitions: [
        [[s, s'], [s, s'], ...];    # partition 1 (by option o; effect cluster 1)
        [[s, s'], [s, s'], ...];    # partition 2 (by option o; effect cluster 2)
        ...                         # partition n (by option o; effect cluster n)
    ]
    """
    effect_partitions = []                                        # result of partitioning by s'

    for mask_partition in mask_partitions: # cluster
        X = [s[2] for s in mask_partitions[mask_partition]]       # reduce X from (s, r, s') to s'
        #TODO determine if the following line can be removed
        # mask = [True, True] + list(mask_partition[2:])            # force x && y to be factors when clustering
        mask = list(mask_partition)
        X = [list(compress(record, mask)) for record in X]        # remove non-masked indices from s'


        n_clusters, labels = cluster(X)
        for i in range(n_clusters):
            X = np.array(mask_partitions[mask_partition])         # re-instantiate X as [(s,r,s'), ...]
            effect_partitions.append(X[labels == i])

    return effect_partitions


def merge_partitions(effect_partitions):
    """
    Identify and merge clusters that share substantially overlapping initiation sets
    :param effect_partitions: [
        [[s, s'], [s, s'], ...];    # partition 1 (by option o; effect cluster 1)
        [[s, s'], [s, s'], ...];    # partition 2 (by option o; effect cluster 2)
        ...                         # partition n (by option o; effect cluster n)
    ]

    :return: [OptionPartition]
    """
    merges = []
    all_clusters = range(len(effect_partitions))
    for i, j in combinations(all_clusters, 2):   # run nC2 clustering operations on effect_partitions
        p_i = [p[0] for p in effect_partitions[i]]  # extract only s (not s') from ith element
        p_j = [p[0] for p in effect_partitions[j]]  # extract only s (not s') from jth element

        n_clusters, labels = cluster(p_i + p_j)

        # don't let negatively labeled cases screw everything up
        p_i_in_all = len(set(labels[:len(p_i)]) - {-1}) == n_clusters
        p_j_in_all = len(set(labels[len(p_i):]) - {-1}) == n_clusters
        if(p_i_in_all and p_j_in_all):
            merges.append((i,j))

    to_combine = merge_sets(set(all_clusters), merges)       # to_combine contains sets of clusters to be combined
    option_partitions = []

    for combination in to_combine:
        o_partition = OptionPartition()
        for clust_idx in combination:
            o_partition.add_effect_cluster(effect_partitions[clust_idx])
        option_partitions.append(o_partition)
    return option_partitions

# -----------------------------v Main Logic v----------------------------- #

# load in raw data
records = loadmat('DataOnlyBin.mat')
raw_data = []
for i in range(len(records['Data'])):
    r = records['Data'][i]
    raw_data.append((tuple(r.s), r.o, r.r, tuple(r.se)))
option_list = ["grasp_styro", "grasp_spray", "grasp_box", "grasp_bottle", "grasp_lysol", "grasp_blockB", "place_styro", "place_spray", "place_box", "place_bottle", "place_lysol", "place_blockB"]
# option_list = ["place_styro"]

print len(raw_data[0][0])

# perform misc. clustering operations
partitioned_options = {}
for o in option_list:
    mask_partitions = partition_masks([record for record in raw_data if record[1] == o])
    effect_partitions = create_effect_partitions(mask_partitions)
    partitioned_options[o] = merge_partitions(effect_partitions)


# TODO:  work below here is not yet working, extremely slow (50 minute ETC) and potentially not even useful
# save on later computation by performing all merge_on_dim_3 for s
all_s_by_partition = {}
for o in option_list:
    for i in range(len(partitioned_options[o])):
        all_s_by_partition[(o,i)] = merge_on_dim_3(partitioned_options[o][i].data, idx=0)

#pos_data = all_s_by_partition[('interact',0)]

# perform grounding computations
# option_list = ['interact']
for o in option_list:
    for i in range(len(partitioned_options[o])):
        # order svm training data
        pos_data = all_s_by_partition[(o,i)]

        neg_data = [all_s_by_partition[key] for key in all_s_by_partition.keys() if key != (o,i)]
        neg_data = reduce(lambda x,y: x + y, neg_data, [])
        # np.random.shuffle(neg_data)
        # neg_data = neg_data[0:2000]
        labels = [0] * len(neg_data) + [1] * len(pos_data)
        init_svm_data = neg_data + pos_data

        # train magic models
        print o,i
        partitioned_options[o][i].fit_init(init_svm_data, labels)
        print "Completed training init sets for partition: " + str(i)
        partitioned_options[o][i].fit_KDEs()
        print "Completed estimating Kernel Density for partition: " + str(i)
        partitioned_options[o][i].fit_rewards()
        print "Completed training reward model for partition: " + str(i)

# save all option data
root = dirname(dirname(dirname(abspath(__file__))))
pickle.dump(partitioned_options, open(root + "/PPDDL_Generation/locomanipulation_option_data.p", "wb"))

print "Done"

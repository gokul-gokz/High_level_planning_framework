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
import random
import math
import numpy as np                  # left in case helpers.py import is ever removed
from itertools import compress
from os.path import dirname, abspath
#import definitions as d
from helpers import *
from mat2csv import *

# a funtion to read from pickle file
def load_pickle(file):
    f = open(file, 'r')
    plans = []
    cnt = 0
    while 1:
        try:
            cnt += 1
            plan = pickle.load(f)
            if cnt > 19:
                print 'skip'
                continue
            else:
                for step in plan:
                    if isinstance(step, tuple):
                        plans.append(step)

        except EOFError:
            print 'load '+ str(len(plans)) + ' plans'
            break

    return plans


# ------------------------v Partitioning Steps v------------------------ #
def partition_masks(option_training_data):
    """
    given the raw training data for a given option, partition based on mask
    :param option_training_data: list of data matching [(s, o, r, s'), (s, o, r, s'), ...]
    :return: a dictionary mapping mask to a corresponding subset of the input {[bool]: [(s,o,r,s'), (s,o,r,s'), ...]}
    """

    partitions = {}       # maps mask (as int) to set of records
    for old, o, r, new in option_training_data:

        #
        ## you may need to change 15 as the threshold
        #mask = tuple([abs(old[idx] - new[idx]) >= 15 for idx in range(len(old))])

        mask = ()
        threshold = 0.0001
        for idx in range(len(old)):
            if isinstance(old[idx],bool):
                #if the state flips: true
                mask += (old[idx]!=new[idx],)
            else: #default is number
                mask += (abs(old[idx] - new[idx]) >= threshold,)

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
        mask = list(mask_partition)
        X = [list(compress(record, mask)) for record in X]        # remove non-masked indices from s'


        n_clusters, labels = cluster(X)
        for i in range(n_clusters):
            X = np.array(mask_partitions[mask_partition])         # re-instantiate X as [(s,r,s'), ...]
            effect_partitions.append(X[labels == i])

    return effect_partitions


def merge_partitions(effect_partitions, merge_flag=True):
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
    if merge_flag:
        for i, j in combinations(all_clusters, 2):   # run nC2 clustering operations on effect_partitions
            p_i = [p[0] for p in effect_partitions[i]]  # extract only s (not s') from ith element
            p_j = [p[0] for p in effect_partitions[j]]  # extract only s (not s') from jth element

            n_clusters, labels = cluster(p_i + p_j)

            if n_clusters > 0:
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

def partition_masks_dynamic(option_training_data, option_partitions,raw_data):
    """
    given the raw training data for a given option, partition based on mask
    :param option_training_data: list of data matching [(s, o, r, s'), (s, o, r, s'), ...]
    :return: a dictionary mapping mask to a corresponding subset of the input {[bool]: [(s,o,r,s'), (s,o,r,s'), ...]}
    """

    partitions = {}  # maps mask (as int) to set of records
    for record in option_training_data:
        old = raw_data[record[4] + 1][0]
        o = raw_data[record[4] + 1][1]
        new = raw_data[record[4] + 1][3]
        mask = ()
        threshold = 0.0001
        for idx in range(len(old)):
            if isinstance(old[idx], bool):
                # if the state flips: true
                mask += (old[idx] != new[idx],)
            else:  # default is number
                mask += (abs(old[idx] - new[idx]) >= threshold,)

        # dynamic_mask = [o+str(i) for i, partition in enumerate(option_partitions[o]) if partition.mask[0] == mask]

        dynamic_mask = None
        for i, partition in enumerate(option_partitions[o]):
            mask_d = set('s'+str(j+1) for j, x in enumerate(mask) if x)
            mask_s = set('s'+str(j+1) for j, x in enumerate(partition.mask[0]) if x)
            if mask_d == mask_s:
                dynamic_mask = o+str(i)
            elif mask_d.issubset(mask_s) and not dynamic_mask:
                dynamic_mask = o+str(i)

        if dynamic_mask:
            if dynamic_mask not in partitions.keys():
                partitions[dynamic_mask] = []
            partitions[dynamic_mask].append((record[0], record[2], record[3]))

    partitionList = []
    o_partition = OptionPartition()
    for key in partitions.keys():
        o_partition.add_effect_cluster(partitions[key], nextOpt=key)
    partitionList.append(o_partition)

    return partitionList

# -----------------------------v Main Logic v----------------------------- #


raw_data = load_pickle('All_C_Records.p')

scaled_data = scaleTableData(raw_data)

static_option_list = ['place', 'pick']
dynamic_option_list = ['move']

# perform misc. clustering operations
partitioned_options = {}

for o in static_option_list:
    mask_partitions = partition_masks([record for record in scaled_data if record[1] == o])
    effect_partitions = create_effect_partitions(mask_partitions)
    partitioned_options[o] = merge_partitions(effect_partitions, merge_flag=False)

for o in dynamic_option_list:
    dynamic_option_data = [record+(index,) for index, record in enumerate(scaled_data) if record[1] == o]
    partitioned_options[o] = partition_masks_dynamic(dynamic_option_data, partitioned_options, scaled_data)
    # dynamic_effect_partitions = create_effect_partitions(dynamic_mask_partitions)
    # partitioned_options[o] = merge_partitions(dynamic_effect_partitions)


# save on later computation by performing all merge_on_dim_3 for s
all_s_by_partition = {}
for o in static_option_list+dynamic_option_list:
    for i in range(len(partitioned_options[o])):
        all_s_by_partition[(o,i)] = merge_on_dim_3(partitioned_options[o][i].data, idx=0)


# perform grounding computations
for o in static_option_list+dynamic_option_list:
    for i in range(len(partitioned_options[o])):
        # order svm training data
        pos_data = all_s_by_partition[(o,i)]

        neg_data = [all_s_by_partition[key] for key in all_s_by_partition.keys() if key != (o,i)]
        neg_data = reduce(lambda x,y: x + y, neg_data, [])
        # neg_data = random.sample(neg_data, len(pos_data))
        labels = [0] * len(neg_data) + [1] * len(pos_data)
        init_svm_data = neg_data + pos_data

        # train magic models
        print o,i
        # partitioned_options[o][i].fit_init(init_svm_data, labels)
        # print "Completed training init sets for partition: " + str(i)
        partitioned_options[o][i].fit_KDEs()
        print "Completed estimating Kernel Density for partition: " + str(i)
        # partitioned_options[o][i].fit_rewards()
        # print "Completed training reward model for partition: " + str(i)

# save all option data
root = dirname(dirname(dirname(abspath(__file__))))
pickle.dump(partitioned_options, open(root + "/PPDDL_Generation/bins_option_data_w_move_tight.p", "wb"))

print "Done"

from itertools import chain, combinations
import numpy as np
from copy import deepcopy
# import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
from itertools import compress
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler

def legible_options(options):
    new_options = {}
    new_nextOption = deepcopy(options['move1'].nextOption)
    for key, option_val in options.iteritems():
        if key != 'move1':
            new_key = ''.join([i for i in key if not i.isdigit()])
            object = [(o+1)/3 for o, val in enumerate(options[key].mask[0][3:])
                      if val and (o+1)%3 == 0]
            new_key = new_key + str(object[0])
            new_options[new_key] = option_val
            for j, opt in enumerate(options['move1'].nextOption):
                if opt == key:
                    new_nextOption[j] = new_key

    new_options['move1'] = options['move1']
    new_options['move1'].nextOption = new_nextOption

    return new_options

def flatten_options(options):

    flat_options = {}
    for part in options.keys():
        for i in range(len(options[part])):
            flat_options[part+str(i+1)] = options[part][i]

    return flat_options

def invert_dict(to_invert):
    """
    inverts a dictionary mapping a scalar to a set by performing join operations on all value sets
    :param to_invert: a dictionary mapping scalars to sets
    :return: an dictionary mapping scalars to sets
    """
    to_return = {}
    for key in to_invert:
        for item in to_invert[key]:
            if item in to_return:
                to_return[item].add(key)
            else:
                to_return[item] = {key}
    return to_return

def all_subsets(iterable, limit=0, notAll = True):
    """
    all_subsets([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3)
    """
    xs = list(iterable)
    if limit == 0:
        max_size = len(xs) + 1
    else:
        max_size = limit
    # note we return an iterator rather than a list
    tuples = chain.from_iterable(combinations(xs, n) for n in range(max_size))
    tmp = map(set, tuples)

    tmp.pop(0)   # remove null combination
    if limit == 0 and notAll:
        tmp.pop(-1)  # remove full combination
    return tmp


def create_start_symb(data):

    params = {'bandwidth': np.logspace(-1, 1, 20)}
    grid = GridSearchCV(KernelDensity(kernel='gaussian'), params)
    imput = np.repeat([data], 10, axis = 0)
    grid.fit(imput)
    return grid.best_estimator_

def project(option, outcome, mask, factors, F):
    """
    returns a groundings for the effect set with any state variables of any factor in factors projected out
    :param option: the option to project factors out of
    :param outcome: The option outcome whose data is used in the projection
    :param factors: the factors that returned groundings cannot be associated with
    :param F: the mapping of factors to state variables
    :return: the KDE instance generated from the projection and the mask associated with the projection
    """
    states = []
    # mask = option.mask[outcome]
    filter_mask = [i for i in mask]
    for f in factors:
        states += F[f]
    for s in states:
        filter_mask[int(s[1:])-1] = False

    outcome_data = option.data[outcome]
    outcome_effects = [s_r_s[2] for s_r_s in outcome_data]
    outcome_effects = [list(compress(record, filter_mask)) for record in outcome_effects]
    params = {'bandwidth': np.logspace(-1, 1, 20)}
    if len(outcome_effects) > 3:
        grid = GridSearchCV(KernelDensity(kernel='gaussian'), params)
        grid.fit(outcome_effects)
        estimator = grid.best_estimator_
    else:
        estimator = KernelDensity(kernel='gaussian')
        estimator.fit(outcome_effects)
    return estimator, filter_mask



def project_symb(symb, symb_mask, o_mask):
    """NOTE, this method does not occur in this example and has not been fully tested"""

    samples = symb.sample(400)
    filter_mask = [symb_mask[i] and not o_mask[i] for i in range(len(symb_mask))]
    overlap_mask = [not o_mask[i] for i in list(compress(xrange(len(symb_mask)), symb_mask))]
    samples = [list(compress(record, overlap_mask)) for record in samples]
    params = {'bandwidth': np.logspace(-1, 1, 20)}
    grid = GridSearchCV(KernelDensity(kernel='gaussian'), params)
    grid.fit(samples)
    to_return = grid.best_estimator_
    return to_return, filter_mask

def remove_duplicates(P, P_masks, refers_to_effect, pfactors):
    """
    removes dictionary values of P which have duplicate groundings.
    For duplicates, combine "refers to effect" so the remaining symbol refers to all relevant effects
    :param P: Dict of KDE groundings associated with each symbol
    :param P_masks: Dict of masks associated with each symbol
    :param refers_to_effect: Dict of options associated with each symbol
    :return: None
    :modifies: Mutates all given dictionaries
    """

    i = 0
    while i < len(P)-1:
        si = "p" + str(i)
        mi = P_masks[si]
        prune_me = []
        if mi[0] != True:
            for j in range(i+1, len(P)):
                sj = "p" + str(j)
                mj = P_masks[sj]
                if (sj not in prune_me) and (mi == mj):
                    pi = P[si]
                    pj = P[sj]
                    if compare_kde(pi, pj, mi, mj):
                        prune_me.append(sj)
                        refers_to_effect[si].append(refers_to_effect[sj][0])
            for to_replace in reversed(prune_me):
                last_ind = 'p' + str(len(P)-1)
                last_p = P.pop(last_ind)
                last_mask = P_masks.pop(last_ind)
                last_ref = refers_to_effect.pop(last_ind)
                last_fac = pfactors.pop(last_ind)
                if not last_ind == to_replace:
                    P[to_replace] = last_p
                    P_masks[to_replace] = last_mask
                    refers_to_effect[to_replace] = last_ref
                    pfactors[to_replace] = last_fac

        # print refers_to_effect[si]
        i = i + 1


def compare_kde(kde1, kde2, mask1, mask2):
    """
    Determines if two KDEs can be considered equivalent but scoring points from each one inside the other
    :param kde1: a KDE instance
    :param kde2: a KDE instance
    :param mask1: the mask for the data in KDE1
    :param mask2: the mask for the data in KDE2
    :return: True if they are "equivalent", False otherwise
    """
    # ensure the variables align
    if not np.array_equal(mask1,mask2):
        return False

    # score samples from KDE2 in KDE1
    data2 = kde2.sample(400)
    scores1 = kde1.score_samples(data2)
    # scores1 = np.exp(kde1.score_samples(data2))
    # means1 = np.mean(scores1)
    fails1 = 0
    for i in range(len(scores1)):
        if scores1[i] < 0.0:
            fails1 = fails1 + 1
    fail_rate1 = float(fails1)/400

    # score samples from KDE1 in KDE2
    data1 = kde1.sample(400)
    scores2 = kde2.score_samples(data1)
    # scores2 = np.exp(kde2.score_samples(data1))
    # means2 = np.mean(scores2)
    fails2 = 0
    for i in range(len(scores2)):
        if scores2[i] < 0.0:
            fails2 = fails2 + 1
    fail_rate2 = float(fails2)/400

    return (fail_rate1 < 0.5) and (fail_rate2 < 0.5)


def combine_kde(kde1, kde2, mask1, mask2):
    """
    takes 2 KDEs and their masks and combines the data into a new KDE
    note: KDES must be over different variables
    :param kde1: a KDE instance
    :param kde2: a KDE instance
    :param mask1: the mask for the data in KDE1
    :param mask2: the mask for the data in KDE2
    :return: The combined KDE and its representative mask
    """
    if kde1 is None or kde2 is None:
        return None, None

    n_samples = 200
    samp1 = kde1.sample(n_samples)
    samp2 = kde2.sample(n_samples)
    both_samples = [samp1, samp2]

    # We need this to ensure that the variables are put into the next KDE in the "proper" order
    data_order = []   # the order in which we will want to pop the samples

    for i in range(len(mask1)):
        if mask1[i]:
            data_order.append(0)
        elif mask2[i]:
            data_order.append(1)
    combined_mask = [mask1[i] or mask2[i] for i in range(len(mask1))]

    #combine the data generated from each KDE
    d = []
    for j in data_order:
        d.append(both_samples[j][:,0])
        both_samples[j] = np.delete(both_samples[j], 0, 1)

    combined_data = np.asarray(d).T

    # generate the new KDE
    params = {'bandwidth': np.logspace(-1, 1, 20)}
    grid = GridSearchCV(KernelDensity(kernel='gaussian'), params)
    grid.fit(combined_data)
    to_return = grid.best_estimator_, combined_mask
    return to_return


def in_init(symbols, symb_masks, Ioi, Ioi_mask):

    agg_kde = symbols[0]
    agg_mask = symb_masks[0]

    index = 1

    while index < len(symbols):
        agg_kde, agg_mask = combine_kde(agg_kde, symbols[index], agg_mask, symb_masks[index])
        if agg_kde is None:
            return False, False

        index = index + 1

    samples = agg_kde.sample(100)
    if not (len(samples[0]) == len(Ioi_mask)):
        return False, False

    # samples = scaler.transform(samples)

    test = Ioi.predict_proba(samples)
    test2 = bool(Ioi.predict([np.mean(samples, axis=0)]))

    testswap = np.swapaxes(test, 0, 1)
    if sum(testswap[1]) > sum(testswap[0]):
        return True, test2
    # for i in test:
    #     if i[1] > i[0]:
    #         pass
    #         print symbols
    # if test2:
    #     print sum(testswap[1]) > sum(testswap[0]), sum(testswap[1]), sum(testswap[0])

    return False, test2


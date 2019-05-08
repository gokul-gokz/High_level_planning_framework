"""
This script contains helper functions and data structures for data_clustering.py which would otherwise
have detracted from the main idea of the file.

As of writing this comment, the bottom 3 functions in OptionPartition [fit_init(), fit_KDEs(), and fit_rewards()]
are currently untested and therefore almost guaranteed to be wrong.

Gunnar Horve <gunnarhorve@gmail.com>
Last Update: 04/30/2018
"""

import numpy as np
import pickle
import time
from itertools import chain, combinations
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import Normalize
from itertools import compress
from scipy.stats import randint as sp_randint
from scipy.stats import expon as sp_expon
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV

from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import RFECV

from sklearn.model_selection import RandomizedSearchCV
from sklearn import svm, datasets
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVR

from sklearn.model_selection import train_test_split

from sklearn.neighbors import KernelDensity
from sklearn.calibration import CalibratedClassifierCV


def merge_sets(all_clusts, merges):
    """
    Condenses a list of sets by combining all sets which can be intersected
    :param all_clusts: The set of all clusters before combining
    :param merges: The list of tuples of each overlapping pair of clusters
    :return: A list of sets of clusters to combine
    """

    def all_subsets(iterable):

        xs = list(iterable)
        # note we return an iterator rather than a list
        tuples = chain.from_iterable(combinations(xs, n) for n in range(len(xs) + 1))
        tmp = map(list, tuples)
        tmp.pop(0)  # remove null combination
        return tmp

    good_ones = []
    for subset in all_subsets(merges)[::-1]:
        subset = [set(i) for i in subset]
        bleh = len(set.intersection(*subset))

        if bleh != 0:
            candidate = set.union(*subset)
            if True not in [candidate.issubset(i) for i in good_ones]:
                good_ones.append(candidate)
                all_clusts = all_clusts - candidate

    for i in all_clusts:
        good_ones.append({i})

    return good_ones


def cluster(X):
    #X_std = StandardScaler().fit_transform(X)

    # #############################################################################
    # Compute DBSCAN
    db = DBSCAN(eps=0.5, min_samples=20).fit(X)
    # core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    # core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    # core_samples = db.core_sample_indices_
    return n_clusters_, np.array(labels)


def merge_on_dim_3(data, idx=0):
    """
    extracts and combines 3rd dimension's nth index from a [][]() structure
        :param data = [outcome1:outcomeN][datum1:datumN](s,r,s')
        :param idx  = which index to extract from 3rd nested dimension
    """
    pos_data = reduce(lambda running_tot, outcomes: running_tot + [s_r_s[idx] for s_r_s in outcomes],
                      data, [])
    return pos_data

class MidpointNormalize(Normalize):

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def scaleTableData(raw_data):
    allx = []
    ally = []
    for sample in raw_data:
        s =sample[0]
        sp = sample[3]
        xs = [s[i] for i in range(len(s))[0::3]] + [sp[i] for i in range(len(s))[0::3]]
        ys = [s[i] for i in range(len(s))[1::3]] + [sp[i] for i in range(len(s))[1::3]]
        allx = allx + xs
        ally = ally + ys
    # scale_data = [[allx[i],ally[i]] for i in range(len(allx))]
    xmax = max(allx)
    xmin = min(allx)
    ymax = max(ally)
    ymin = min(ally)
    maxscale = []
    minscale = []
    for i in range(11):
        maxscale.append(xmax)
        maxscale.append(ymax)
        maxscale.append(True)
        minscale.append(xmin)
        minscale.append(ymin)
        minscale.append(False)
    scaleme = StandardScaler()
    scaleme.fit([maxscale, minscale])
    pickle.dump(scaleme, open("gamescaler.p", "wb"))

    new_raw_data = []
    for sample in raw_data:
        newsample = (tuple(scaleme.transform([sample[0]])[0]), sample[1], sample[2], tuple(scaleme.transform([sample[3]])[0]))
        new_raw_data.append(newsample)

    return new_raw_data



# #############################################################################


##################################################################################

class OptionPartition:
    def __init__(self):
        """
        :param data: an array containing the arrays of data for each possible distinct "outcome" of the option
                    [[outcome 1],[outcome 2]...[outcome n]]
                    Each outcome is [[sample],[sample],[sample]]
                    Note that many options will only have one outcome
        :param prob: an array containing the probability of occurrence for each possible distinct "outcome" of the option
                    [[prob 1],[prob 2]...[prob n]]
        :param init_model: the model representing the initiation set of the option
        :param kde_models: an array containing the models representing the effect set for each outcome of the option
        :param reward_models: an array containing the models representing the reward for each outcome of the option
        """

        self.data = []
        self.prob = []
        self.mask = []
        self.nextOption = []

        self.init_model = None
        self.init_mask = None
        self.init_scaler = None
        self.kde_models = []
        self.reward_models = []

    def add_effect_cluster(self, eff_clust, nextOpt = None):
        np.random.shuffle(eff_clust)
        self.data.append(eff_clust)
        self.nextOption.append(nextOpt)
        tot_points = sum([len(c) for c in self.data])
        tot_points = float(tot_points)  # integer math is sad
        self.prob = [len(c) / tot_points for c in self.data]

        #calculate mask
        threshold = 0.0001
        self.mask.append(tuple([(abs(eff_clust[0][0][idx] - eff_clust[0][2][idx]) >= threshold) for idx in range(len(eff_clust[0][0]))]))


    def find_optimal_params(self, X, Y):
        """
        Takes in a set of data and labels and determines the optimal C and gamma for training an SVM
        :param X: The set of data
        :param Y: The labels of each datapoint
        :return: [C, gamma], best_score
        """
        # Train classifiers
        #
        # For an initial search, a logarithmic grid with basis
        # 10 is often helpful. Using a basis of 2, a finer
        # tuning can be achieved but at a much higher cost.

        C_range = np.logspace(0, 10, 5)
        gamma_range = np.logspace(0, 5, 5)

        # # Extensive grid search
        # param_grid = dict(gamma=gamma_range, C=C_range)
        # cv = StratifiedShuffleSplit(n_splits=3, test_size=0.2, random_state=42)
        # grid = GridSearchCV(svm.SVC(class_weight='balanced', kernel='rbf', probability=True,
        #                             random_state=np.random.RandomState()), n_jobs=6, pre_dispatch="n_jobs", param_grid=param_grid, cv=cv)

        # Randomized search
        param_dist = {'C': C_range, 'gamma': gamma_range, 'kernel': ['rbf'], 'class_weight': ['balanced']}
        grid = RandomizedSearchCV(svm.SVC(class_weight='balanced', kernel='rbf', probability=True,
                                          random_state=np.random.RandomState()), param_distributions=param_dist)
        grid.fit(X, Y)

        print("The best parameters are %s with a score of %0.2f"
              % (grid.best_params_, grid.best_score_))
        return grid.best_params_, grid.best_score_

    def fit_init(self, data, labels):
        """
        Determines which state variables are essential to the initiation set and trains an SVM on them
        Saves the results in self.init_model and self.init_mask
        :param data: The datapoints to be put into the SVM
        :param labels: The labels for the datapoints on whether they are part of this option
        :return: None
        """

        # massage data

        X = np.array(data)
        Y = np.array(labels)
        # scaler = StandardScaler()
        # X = scaler.fit_transform(X)

        # determine optimal parameters for the SVM training
        params, score = self.find_optimal_params(X, Y)      #params is a dict with 'C', 'gamma'

        # Make and train an SVM to produce a base cross validation score
        clf = svm.SVC(C=params['C'], class_weight='balanced', gamma=params['gamma'],
                      kernel='rbf', probability=True, random_state=np.random.RandomState())
        base_score = np.mean(cross_val_score(clf, X, Y, cv=3))

        #---------------------------------------------FEATURE SELECTION-------------------------------------------------

        # Determine which variables are required to keep to provide an accurate classifier
        keep_mask = range(len(data[0]))  # Initialize set of variables to keep as all zeros
        for i in range(len(data[0])):
            keep_mask.remove(i)  # remove the given state variable from the mask
            if len(keep_mask) != 0:
                masked_X = np.array([[sample[j] for j in keep_mask] for sample in data])  # Apply the mask to the data
                # masked_X = scaler.fit_transform(masked_X)  # Scale data

                scores = np.mean(cross_val_score(clf, masked_X, Y, cv=3))  # calculate cross-val score

            if (np.mean(scores) - base_score)/base_score <= -0.01:   # if removing this variable hurt the score, add it back into the mask
                keep_mask.append(i)

        print keep_mask


        # # Best Subset Selection
        # keep_mask = range(len(data[0]))  # Initialize set of variables to keep as all zeros
        # for i in range(len(data[0]) - 1):
        #     scores_list = range(len(keep_mask))
        #     for j in range(len(keep_mask)):
        #         del keep_mask[j]  # remove the given state variable from the mask
        #         masked_X = np.array([[sample[k] for k in keep_mask] for sample in data])  # Apply the mask to the data
        #         # masked_X = scaler.fit_transform(masked_X)  # Scale data
        #
        #         scores = np.mean(cross_val_score(clf, masked_X, Y, cv=3))  # calculate cross-val score
        #         clf.fit(masked_X, Y)
        #         # print i, scores
        #         scores_list[j] = np.mean(scores)
        #         keep_mask.insert(j,j)
        #
        #     del keep_mask[np.argmin(scores_list)]
        #
        #     if np.argmin(scores_list) > base_score:
        #         final_keep = keep_mask
        #         base_score = np.argmin(scores_list)
        #
        # print keep_mask

        # if not keep_mask:
        #     keep_mask = range(len(data[0]))

        #---------------------------------------------------------------------------------------------------------------

        # Apply the final mask and save the resulting classifier SVM
        masked_X = np.array([[sample[j] for j in keep_mask] for sample in data])
        # masked_X = scaler.fit_transform(masked_X)
        # self.init_scaler = scaler

        param_dist = {'C': sp_expon(scale=100), 'gamma': sp_expon(scale=.1),
                      'kernel': ['rbf'], 'class_weight': ['balanced']}
        grid = RandomizedSearchCV(svm.SVC(class_weight='balanced', kernel='rbf', probability=True,
                                          random_state=np.random.RandomState()), param_distributions=param_dist)
        grid.fit(masked_X, Y)

        clf_platt = CalibratedClassifierCV(grid.best_estimator_, cv='prefit', method='sigmoid')
        clf_platt.fit(masked_X, Y)

        self.init_mask = keep_mask
        self.init_model = clf_platt


    def fit_init_factors(self, data, labels, factors, F):
        """
        Determines which state variables are essential to the initiation set and trains an SVM on them
        Saves the results in self.init_model and self.init_mask
        :param data: The datapoints to be put into the SVM
        :param labels: The labels for the datapoints on whether they are part of this option
        :param factors: The factors of the task
        :return: None
        """

        # massage data
        X = np.array(data)
        Y = np.array(labels)

        # # determine optimal parameters for the SVM training
        # params, score = self.find_optimal_params(X, Y)      #params is a dict with 'C', 'gamma'
        #
        # # Make and train an SVM to produce a base cross validation score
        # clf = svm.SVC(C=params['C'], class_weight='balanced', gamma=params['gamma'],
        #               kernel='rbf', probability=True, random_state=np.random.RandomState())
        # base_score = np.mean(cross_val_score(clf, X, Y, cv=3))
        # min_score = base_score
        #
        # # -------------------------------------------FEATURE SELECTION------------------------------------------------ #
        # # Determine which variables are required to keep to provide an accurate classifier
        # keep_mask = []  # Initialize set of variables to keep as all zeros
        # for key in factors.keys():
        #     for i in [int(s[1:]) for s in factors[key]]:
        #         keep_mask.append(i-1)
        #
        # for key in factors.keys():
        #     for i in [int(s[1:]) for s in factors[key]]:
        #         keep_mask.remove(i-1)  # remove the given state variable from the mask
        #     if len(keep_mask) != 0:
        #         masked_X = np.array([[sample[j] for j in keep_mask] for sample in data])  # Apply the mask to the data
        #         scores = np.mean(cross_val_score(clf, masked_X, Y, cv=3))  # calculate cross-val score
        #
        #     # if (np.mean(scores) - base_score)/base_score <= -0.01:
        #     #     for i in [int(s[1:]) for s in factors[key]]:
        #     #         keep_mask.append(i-1)
        #
        #         if scores < base_score:
        #             print "score", scores, "base", base_score
        #             for i in [int(s[1:]) for s in factors[key]]:
        #                 keep_mask.append(i - 1)
        #             if scores < min_score:
        #                 min_score = scores
        #                 min_key = key
        #
        # # HARD-CODED ASSIGNMENT FOR PICK & PLACE
        # keep_mask = [0]
        # for i in [int(s[1:]) for s in factors[min_key]]:
        #     keep_mask.append(i-1)
        # keep_mask.sort()
        # print keep_mask

        # ------------------------------------------------------------------------------------------------------------ #

        keep_mask = [0, 2]
        factor_list = [f for f in F if f != 'f3']
        for i in [int(s[1:]) for s in factors[factor_list[0]]]:
            keep_mask.append(i-1)
        keep_mask.sort()

        print keep_mask

        # Apply the final mask and save the resulting classifier SVM
        masked_X = np.array([[sample[j] for j in keep_mask] for sample in data])
        # masked_X = scaler.fit_transform(masked_X)
        # self.init_scaler = scaler

        param_dist = {'C': sp_expon(scale=100), 'gamma': sp_expon(scale=.1),
                      'kernel': ['rbf'], 'class_weight': ['balanced']}
        grid = RandomizedSearchCV(svm.SVC(class_weight='balanced', kernel='rbf', probability=True,
                                          random_state=np.random.RandomState()), param_distributions=param_dist)
        grid.fit(masked_X, Y)

        clf_platt = CalibratedClassifierCV(grid.best_estimator_, cv='prefit', method='sigmoid')
        clf_platt.fit(masked_X, Y)

        self.init_mask = keep_mask
        self.init_model = clf_platt

    def fit_KDEs(self):
        self.kde_models = []
        for i in range(len(self.data)):
            outcome = self.data[i]
            outcome_effects = [s_r_s[2] for s_r_s in outcome]
            outcome_effects = [list(compress(record, self.mask[i])) for record in outcome_effects]
            params = {'bandwidth': np.logspace(-1.5, 1.5, 20)}
            if len(self.data[i]) > 3:
                grid = GridSearchCV(KernelDensity(kernel='gaussian'), params)
                grid.fit(outcome_effects)
                estimator = grid.best_estimator_
            else:
                estimator = KernelDensity(kernel='gaussian')
                estimator.fit(outcome_effects)
            # test = grid.best_estimator_.sample(20)
            self.kde_models.append(estimator)

    def fit_rewards(self):
        self.reward_models = []
        for outcome in self.data:
            X = [s_r_s[0] for s_r_s in outcome]
            Y = [s_r_s[1] for s_r_s in outcome]

            param_grid = {'C': np.logspace(0, 10, 20), 'gamma': np.logspace(0, 1, 20)}
            grid_search = GridSearchCV(SVR(kernel='rbf'), param_grid, cv=3)
            grid_search.fit(X, Y)

            self.reward_models.append(grid_search.best_estimator_)




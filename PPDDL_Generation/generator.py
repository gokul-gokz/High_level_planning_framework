"""
Ideally, will be a retooled version of PDDL_Generation.py that takes input from data_clustering.py.

Most lines have not yet been changed, as this is a work in progress

Max Merlin
Last Update: 06/08/2018

"""
import os
import itertools
import pickle
from helpers import *
from sklearn.preprocessing import StandardScaler

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate(partitioned_options):
    """
    This is an implementation of "Algorithm 1: Generate a PDDL Domain Description From Characterizing Sets" found in
    http://irl.cs.brown.edu/pubs/orig_sym_jair.pdf (Konidaris, Kaelbling, Lozano-Perez)
    This is updated to work for PPDDL (probabilistic PDDL)

    It converts direct options and their effects to an equivalent PPDDL description.

    :param masks:           a dictionary mapping option names to a boolean list of possibly affected state variables
    :param initiation_set:  a dictionary mapping option names to a list of groundings describing the set of states from
                                which the option can be performed
    :param effect_set:      a dictionary mapping option names to a list of groundings describing the set of states
                                which could result from performing said option
    :param groundings:      a dictionary mapping grounding names to grounding tests

    :return: P:             a dictionary mapping generated symbol names to a set of groundings
             effects_plus:  a dictionary mapping option names to a list of symbols to be set to TRUE when an option
                                is performed
             effects_less:  a dictionary mapping option names to a list of symbols to be set to FALSE when an option
                                is performed
             preconditions: a dictionary mapping option names to a list of symbols that must be TRUE before an option
                                can be performed
    """
    # ------------------------Massage Given Data----------------------------------
    flat_options = flatten_options(partitioned_options)

    flat_options = legible_options(flat_options)

    # convert masks into more preferable format
    modifies = {}
    for option in flat_options:
        for j in range(len(flat_options[option].mask)):
            str_mask = set()
            for i in range(len(flat_options[option].mask[j])):
                if flat_options[option].mask[j][i]:
                    str_mask.add('s' + str(i + 1))
            modifies[option + "_" + str(j)] = str_mask

    modifies = invert_dict(modifies)

    # ------------------------Compute Factors----------------------------------
    F = {}          # maps f's to {s}
    options = {}    # maps f's to {o}

    # Compute Factors
    for si in modifies:
        new_factor = True
        for fj in F:
            if options[fj] == modifies[si]:
                F[fj] = F[fj] | {si}        # update F mapping
                new_factor = False
        if new_factor:
            fj = 'f' + str(len(F) + 1)
            F[fj] = {si}                    # create new F mapping
            options[fj] = modifies[si]      # create new options mapping


    # ------------------------Generate Symbol Set----------------------------------
    factors = invert_dict(options)          # maps o's to {f}
    inv_F = invert_dict(F)                  # maps s's to {f}
    pfactors = {}                           # maps p's to {f}
    P = {}                                  # maps p's to {g}
    P_masks = {}                            # stores masks of p's
    refers_to_effect = {}                   # maps p's to o

    # # create symbols for start state of game
    starts = [[0.1029, 1.0, -1.0, -0.7959, -0.4101, -1.0, -0.6165, -0.4101, -1.0, -0.437,  -0.4101, -1.0, -0.2576,  -0.4101, -1.0, -0.0782,  -0.4101, -1.0,  0.2807,  -0.4101, -1.0, 0.4601,  -0.4101, -1.0,  0.6395,  -0.4101, -1.0,  0.8189, -0.4101, -1.0,  1.0,  -0.4101, -1.0],
             [0.1029, 1.0, -1.0, -0.7959, 0.0562, -1.0, -0.6165, 0.0562, -1.0, -0.437,  0.0562, -1.0, -0.2576,  0.0562, -1.0, -0.0782,  0.0562, -1.0,  0.2807,  0.0562, -1.0, 0.4601,  0.0562, -1.0,  0.6395,  0.0562, -1.0,  0.8189, 0.0562, -1.0,  1.0,  0.0562, -1.0],
             [0.1029, 1.0, -1.0, -0.7959, 0.5225, -1.0, -0.6165, 0.5225, -1.0, -0.437,  0.5225, -1.0, -0.2576,  0.5225, -1.0, -0.0782,  0.5225, -1.0,  0.2807,  0.5225, -1.0, 0.4601,  0.5225, -1.0,  0.6395,  0.5225, -1.0,  0.8189, 0.5225, -1.0,  1.0,  0.5225, -1.0]]


    for factor in F:
        mask = list(np.repeat(False, 33))
        for s in F[factor]:
            mask[int(s[1:]) - 1] = True

        for s in starts:
            factor_data = list(compress(s, mask))
            start_est = create_start_symb(factor_data)
            pi = 'p' + str(len(P))
            P[pi] = start_est
            P_masks[pi] = mask
            pfactors[pi] = {factor}
            refers_to_effect[pi] = [None]


    # create symbols for each option
    for oi in factors:
        f = factors[oi]
        oi_name = oi[:oi.index('_')]
        oi_outcome = int(oi[oi.index('_')+1:])
        oi_mask = flat_options[oi_name].mask[oi_outcome]
        # print oi_name, oi_outcome
        e = flat_options[oi_name].kde_models[oi_outcome]

        for fi in f:  # factor out independent factors
            proj_fi = None
            fi_mask = None
            equivalent = False

            proj_not_fi, not_fi_mask = project(flat_options[oi_name], oi_outcome, oi_mask, factors[oi] - {fi}, F)
            if len(f) > 1:
                proj_fi, fi_mask = project(flat_options[oi_name], oi_outcome, oi_mask, {fi}, F)

                # combine proj_fi and proj_not_fi and compare with e
                combined_kde, combined_mask = combine_kde(proj_fi, proj_not_fi, fi_mask, not_fi_mask)

                equivalent = compare_kde(combined_kde, e, combined_mask, oi_mask)

            if equivalent or (len(f) < 2):   # make symbols for only independent factors
                pi = 'p' + str(len(P))
                P[pi] = proj_not_fi
                P_masks[pi] = not_fi_mask
                e = proj_fi                     # remove independent factors for later iterations of this loop
                oi_mask = fi_mask
                f = f - {fi}
                pfactors[pi] = {fi}
                refers_to_effect[pi] = [oi]

        if len(f) > 0:
            for fs in all_subsets(f, notAll = False):           # make symbols for all sets of non-independent factors
                pi = 'p' + str(len(P))
                P[pi], P_masks[pi] = project(flat_options[oi_name], oi_outcome, oi_mask, f - fs, F)
                pfactors[pi] = fs
                if len(fs) == len(f):
                   refers_to_effect[pi] = [oi]
                else:
                    refers_to_effect[pi] = [None]

    print "symbols generated"

    remove_duplicates(P, P_masks, refers_to_effect, pfactors)  # Prune duplicates and null sets from symbols

    # ------------------------Generate Operator Descriptions----------------------------------
    effects_plus = dict.fromkeys(factors.keys(), set())        # maps oi to {p}
    effects_less = dict.fromkeys(factors.keys(), set())        # maps oi to {p}
    cond_effects = dict.fromkeys(factors.keys(), set())        # maps oi to {p}
    preconditions = dict.fromkeys(flat_options.keys(), [])     # maps oi to {p}

    # Assign symbols to effects
    for oi in factors:
        if oi[:4] != 'move':      #EFFECTS ARE NOT ASSIGNED TO DYNAMIC OPTION PARTITIONS
            # positive effects
            for p in P.keys():
                if oi in refers_to_effect[p]:
                    effects_plus[oi] = effects_plus[oi] | {p}

            Pnr = set(P.keys()) - effects_plus[oi]

            # negative effects: full overwrites
            for p in Pnr:
                if(#P[p].issubset(initiation_set[oi]) and
                   pfactors[p].issubset(factors[oi])):      #TODO P[p].issubset(initiation_set[oi])
                    effects_less[oi] = effects_less[oi] | {p}

            Pnr = Pnr - effects_less[oi]

            # conditional effects: partial overwrites
            #TODO check if p1 is in Ioi
            #TODO this section takes way too long (3-4 hours) so its being commented until the above check can be evaluated
            # for p1, p2 in itertools.permutations(Pnr, 2):           # Get all 2-long permutations of Pnr-->O(N^2)
            #     a = len(pfactors[p1] & factors[oi])
            #     if not (len(pfactors[p1] & factors[oi]) == 0):       # if p1 partially overlaps with factors of oi
            #         kde, mask = project_symb(P[p1], P_masks[p1], flat_options[oi[:-2]].mask[int(oi[-1])])
            #         if compare_kde(kde, P[p2], mask, P_masks[p2]):
            #             cond_effects[oi] = cond_effects[oi] | {(p1, p2)}

    print "symbols assigned to effects"

    #-----------------Evaluate init groundings using factors-----------------------
    all_s_by_partition = {}
    for o in flat_options.keys():
        all_s_by_partition[o] = reduce(lambda running_tot, outcomes: running_tot + [s_r_s[0] for s_r_s in outcomes],
                          flat_options[o].data, [])

    for o in flat_options.keys():
        if o[:4] != 'move':
            print o
            pos_data = all_s_by_partition[o]
            neg_data = [all_s_by_partition[key] for key in all_s_by_partition.keys() if key != o]
            neg_data = reduce(lambda x,y: x + y, neg_data, [])
            labels = [0] * len(neg_data) + [1] * len(pos_data)
            init_svm_data = neg_data + pos_data

            flat_options[o].fit_init_factors(init_svm_data, labels, F, factors[o+'_0'])

    pickle.dump(flat_options, open(root + "/Locomanipulation Task/PPDDL_Generation/flat_options_w_initSVMs_legible.p", "wb"))


    # evaluate preconditions
    flat_options = pickle.load(open(root + "/Locomanipulation Task/PPDDL_Generation/flat_options_w_initSVMs_legible.p", "rb"))
    for oi in flat_options:

        # compute preconditions
        Ioi_mask = flat_options[oi].init_mask
        Ioi = flat_options[oi].init_model
        if Ioi == None:
            preconditions[oi] = [set([])]
            continue
        relevant_factors = set([list(inv_F['s' + str(i+1)])[0] for i in Ioi_mask])
        relevant_symbols = filter(lambda p:
                                  reduce((lambda x, y: x or (y in relevant_factors)), pfactors[p], False),  # Ioi contains some subset of P[p]
                                  P.keys())

        for Pc in all_subsets(relevant_symbols, limit=len(relevant_factors)+1):
            # compute variables for checks
            # Ioi_s = {"s" + str(groundings[g]["var_num"]) for g in Ioi}
            # Ioi_factors = {list(inv_F[s])[0] for s in Ioi_s}
            # g_list = {g for p in Pc for g in P[p]}
            Pc_factors = [f for p in Pc for f in pfactors[p]]

            test = (len(Pc_factors) == len(set(Pc_factors)))

            if not (len(Pc_factors) == len(set(Pc_factors)) and        # Checks that there are no redundant factors in Pc
                    relevant_factors.issubset(set(Pc_factors))):    # Checks that the initiation set of oi is within Pc
                continue

            G_in_Ioi, G_in_Ioi2 = in_init([P[i] for i in Pc], [P_masks[symbol] for symbol in Pc], Ioi, Ioi_mask)
            if G_in_Ioi2 and oi[:4] == 'pick':
                preconditions[oi] = preconditions[oi] + [Pc]
            if G_in_Ioi and oi[:5] == 'place':                         # Checks that the groundings of Pc is within init set of oi
                preconditions[oi] = preconditions[oi] + [Pc]  # TODO: Allow for multiple pc sets of preconditions
        print oi

    print "Done"

    return P, P_masks, effects_plus, effects_less, preconditions

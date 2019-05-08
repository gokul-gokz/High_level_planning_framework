from PPDDL_Generation.helpers import *
import numpy as np

reachRange = 300.0
y_offest = 386.0

def get_reachability(x,y):
    """
    given an x,y coordinate of an object, calculates the max and min x coordinates
    from which a robot with range reachRange and y 0 could reach the object
    :param x: pretty obvious
    :param y: give it your best guess
    :return: min x, max x
    """

    h = ((reachRange-(y-y_offest))/reachRange)
    angle = 2 * np.arccos(1-h)

    halfChord = reachRange * np.sin(angle/2)

    return x - halfChord, x + halfChord

def get_reachabilities(ll_in):
    """
    given a low level state, evaluates the reachability of each object and subsequent spaces of shared reachability.
    :param ll_in: list of x,y coordinates of objects
    :return: the midpoints of each segment with unique reachability

    """

    #extract the x,y values from state vector
    obj_locs = []
    for i in range(len(ll_in)):
        if not ((i % 3) == 2) and i > 2:
            obj_locs.append(ll_in[i])

    #get the min and max x value from which each object can be reached
    can_reach = []
    for i in range(len(obj_locs)/2):
        min, max = get_reachability(obj_locs[2 * i], obj_locs[2 * i + 1])
        can_reach.append(min)
        can_reach.append(max)

    #find overlap of regions of reachability
    sortedDists = sorted(list(can_reach))

    # #determine what can be reached from each segment
    # reach_segs = []
    # reachables = []
    # for i in range(len(sortedDists)-1):
    #     point = sortedDists[i]
    #     ind = can_reach.index(point)
    #     if (ind % 2) == 0:
    #         reachables.append(ind/2)
    #     else:
    #         reachables.remove(ind/2)
    #
    #     reach_segs.append(set(reachables))

    # find the midpoint of each segment of reachability to output as a low level movement goal
    midpoints = []
    for i in range(len(sortedDists)-1):
        midpoints.append(np.mean([sortedDists[i], sortedDists[i+1]]))

    return midpoints

    # return reach_segs, sortedDists


def convert_to_HL(ll_state, P, pmasks):
    """
    takes a full low level world state and evaluates which high level symbols would be true for that state
    :param ll_state: the low level state
    :param P: the list of symbols
    :param pmasks:  the masks of each symbol
    :return: hl_state: the list of symbols representing the input low level state
    """
    hl_state = set([])
    for symbol_name in P.keys():
        masked_state = [i for i in compress(ll_state, pmasks[symbol_name])]

        istrue = 0 < P[symbol_name].score_samples([masked_state])
        if istrue:
            hl_state.add(symbol_name)

    # print(hl_state)
    return set(hl_state)


# ans = gen_ll_states([-30,40,0,70,20,60])
# # ans = get_reachability(0,50)
#
# print "test"


def descale(scaler, state_vec):
    scale_vec = scaler.inverse_transform([state_vec])
    return scale_vec[0]


def apply_scale(scaler, state_vec):
    scale_vec = scaler.transform([state_vec])
    return scale_vec[0]

def find_move_parts(midpoints, P, P_masks, scaler):
    """
    specificlly used for finding the positive and negative effects for the dynamic move option.
    :param midpoints: The low level locations the robot would consider moving to
    :param P: the symbols of the task
    :param P_masks: the symbols masks
    :param scaler: gotta scale that data baby
    :return: partitions: a list of all possible outcomes of performing a move option, each outcome is in the format
                        [[effects+], [effects-], location] where location is the low level selected (unscaled) point
                        that is being moved to.
    """

    partitions = []

    # determine which symbols are over the variable changed by moving, store in move_symbols
    move_symbols = []
    for symb in P.keys():
        if P_masks[symb][0] == 1:
            move_symbols.append(symb)

    # iterate through locations to move to, scale them, evaluate which symbols become true or false as result
    for loc in midpoints:
        eff_plus = set([])
        eff_minus = set([])
        scale_vec = np.zeros(33)
        scale_vec[0] = loc
        scaled_loc = scaler.transform([scale_vec])[0]
        for symb in move_symbols:
            istrue = 0 < P[symb].score_samples([[scaled_loc[0]]])
            if istrue:
                eff_plus.add(symb)
            else:
                eff_minus.add(symb)
        partitions.append([eff_plus, eff_minus, loc])

    return partitions

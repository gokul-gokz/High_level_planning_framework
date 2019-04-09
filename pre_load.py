import pickle

from game.data_generation.helpers import *
from plan_helpers import *

def init(initiWorldState):
    global PDDL_data
    PDDL_data = pickle.load(open("PPDDL_Generation/PDDL_Domains/bins_PDDL_C_2.p", "rb"))
    # PDDL_data = pickle.load(open("PPDDL_Generation/option_data.p", "rb"))
    global scaler
    scaler = pickle.load(open("game/data_generation/gamescaler.p", "rb"))

    global P
    P = PDDL_data['P']
    global pmasks
    pmasks = PDDL_data['pmasks']
    global effects_plus
    effects_plus= PDDL_data['effects_plus']
    global effects_less
    effects_less = PDDL_data['effects_less']
    global preconditions
    preconditions = PDDL_data['preconditions']
    print preconditions

    # this is a placeholder, it will take in from game
    global startState
    startState = [0.1029, 1.0, -1.0, -0.7959, 0.5225, -1.0, -0.6165, 0.5225, -1.0, -0.437, 0.0562, -1.0, -0.2576,
                  0.0562, -1.0, -0.0782, -0.4101, -1.0, 0.2807, 0.5225, -1.0, 0.4601, -0.4101, -1.0, 0.6395, 0.0562,
                  -1.0, 0.8189, -0.4101, -1.0, 1.0, 0.5225, -1.0]
    startState = apply_scale(scaler, initiWorldState)
    #print startState
    #print type(startState)
    #print type(startState[0])
    global move_points
    move_points = get_reachabilities(descale(scaler, startState))
    global move_partitions
    move_partitions = find_move_parts(move_points, P, pmasks, scaler)

    preconditions['move1'] = [set([])]
    global hl_start
    hl_start = convert_to_HL(startState, P, pmasks)
    global hl_end
    # Object symbols
    #p1- object 4
    #p16- object 5
    #p37- object 1
    #p39- object 7
    #p42- object 3
    #p44- object 9
    #p53- object 0
    #hl_end = set(['p44', 'p53', 'p37', 'p70', 'p42', 'p1', 'p16', 'p64', 'p39', 'p63'])

    hl_end=set(['p53','p1'])
    hl_start = hl_start - hl_end
    print"Goal:"
    print"Object 0 and Object 4 should be inside the bin"

if __name__ == '__main__':
    initWorldState = (154, 314, False, 263, 314, False, 372, 314, False, 481, 314, False, 590, 314, False, 669, 188, False, 808, 314, False, 917, 314, False, 1026, 314, False, 1135, 314, False, 1245, 314, False)
    init(initWorldState)

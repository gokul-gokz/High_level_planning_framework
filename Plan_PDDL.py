from game.data_generation.helpers import *
from plan_helpers import *

PDDL_data = pickle.load(open("PPDDL_Generation/PDDL_Domains/bins_PDDL_C_2.p", "rb"))
# PDDL_data = pickle.load(open("PPDDL_Generation/option_data.p", "rb"))
scaler = pickle.load(open("game/data_generation/gamescaler.p", "rb"))

P = PDDL_data['P']
pmasks = PDDL_data['pmasks']
effects_plus = PDDL_data['effects_plus']
effects_less = PDDL_data['effects_less']
preconditions = PDDL_data['preconditions']

#run the game

# this is a placeholder, it will take in from game
startState = [0.1029, 1.0, -1.0, -0.7959, 0.5225, -1.0, -0.6165, 0.5225, -1.0, -0.437,  0.0562, -1.0, -0.2576,  0.0562, -1.0, -0.0782,  -0.4101, -1.0,  0.2807,  0.5225, -1.0, 0.4601,  -0.4101, -1.0,  0.6395,  0.0562, -1.0,  0.8189, -0.4101, -1.0,  1.0,  0.5225, -1.0]
#endState = [0.1029, 1.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0,  0.0, 0.0, -1.0, 0.0, 0.0, -1.0,  0.0, 0.0, -1.0,  0.0, 0.0, -1.0,  0.0, 0.0, -1.0]
move_points = get_reachabilities(descale(scaler, startState))
move_partitions = find_move_parts(move_points, P, pmasks, scaler)

preconditions['move1'] = [set([])]
hl_start = convert_to_HL(startState, P, pmasks)
# hl_end = convert_to_HL(endState, P, pmasks)
hl_end = set(['p44', 'p53', 'p37', 'p70', 'p42', 'p1', 'p16', 'p64', 'p39', 'p63'])
hl_start = hl_start - hl_end

class Proposition:
    def __init__(self, symb_list, prec_option, parent, param):
        self.symb_list = frozenset(symb_list)
        self.prec_option = prec_option
        self.parent = parent
        self.param = param

    def get_neighbors(self, visited):
        neighbors = []
        for o in preconditions:
            isIn = False
            for pre in preconditions[o]:

                if pre.issubset(self.symb_list):
                    isIn = True
                    break
            if isIn:
                if 'move' in o:
                    for loc in move_partitions:
                        new_prop = Proposition((self.symb_list | loc[0]) - loc[1], o, self, loc[2])
                        if new_prop.symb_list not in visited:
                            visited.add(frozenset(new_prop.symb_list))
                            neighbors.append(new_prop)
                else:
                    for outcome in [val for i, val in enumerate(effects_plus.keys()) if o == val[:val.index('_')]]:
                        for p in effects_plus[outcome]:
                            if True in pmasks[p][3:]:
                                obj = (pmasks[p].index(True)) / 3
                        new_prop = Proposition((self.symb_list | effects_plus[outcome]) - effects_less[outcome], outcome, self, obj)

                        if new_prop.symb_list not in visited:
                            visited.add(frozenset(new_prop.symb_list))
                            neighbors.append(new_prop)

        return neighbors


def bfs(start, goal):
    start_time = time.time()

    queue = [Proposition(start, None, None, None)]
    cur = queue.pop()
    visited = {frozenset(cur.symb_list)}

    while not goal.issubset(cur.symb_list):
        queue = queue + cur.get_neighbors(visited)
        if len(queue) == 0:
            print "no solution found"
            break
        cur = queue.pop(0)     # this will break if there is no solution
    res, par = backtrace(cur)

    end_time = time.time()

    #execute the plan.
    #res is the option
    #par is the parameters


    print "visited length: ", len(visited)
    print "Elapsed time: ", end_time - start_time, "seconds"
    if not(len(queue) == 0):
        print res
        print ""
        print par
        return res, par
    else:
        print "max depth explored: ", len(res)
        return


def backtrace(cur):
    opt_list = []
    opt_params = []
    while not cur.prec_option == None:
        opt_list.append(cur.prec_option)
        opt_params.append(cur.param)
        cur = cur.parent

    return opt_list[::-1], opt_params[::-1]

path = bfs(hl_start, hl_end)

print 'blep'

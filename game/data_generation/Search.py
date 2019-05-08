import time
import pickle
import os
import definitions as d
from helpers import *

import PPDDL_Generation.generator as ppddl_gen

# common data to test
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
partitioned_options = pickle.load(open(root + "/PPDDL_Generation/bins_option_data_w_move_tight.p", "rb"))

P, pmasks, effects_plus, effects_less, preconditions = ppddl_gen.generate(partitioned_options)
PDDL = {}
PDDL['P'] = P
PDDL['pmasks'] = pmasks
PDDL['effects_plus'] = effects_plus
PDDL['effects_less'] = effects_less
PDDL['preconditions'] = preconditions

pickle.dump(PDDL, open(root + "/PPDDL_Generation/PDDL_Domains/bins_PDDL_C_2.p", "wb"))

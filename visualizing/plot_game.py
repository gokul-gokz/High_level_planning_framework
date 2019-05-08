import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pickle
import numpy as np
import os
import sys
from copy import deepcopy

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root+"/Locomanipulation Task/game/data_generation")
from helpers import *

the_scaler = pickle.load(open(root + "/Locomanipulation Task/game/data_generation/gamescaler.p", "rb"))
partitioned_options = pickle.load(open(root + "/Locomanipulation Task/PPDDL_Generation/bins_option_data_w_move_tight.p", "rb"))


def plot_symbols(prev_scaler):
    f = open('norm_temp_output.p')
    (P, P_masks) = pickle.load(f)
    f.close()

    P_val = {}
    for p in P:
        smp = np.mean(P[p].sample(1000), axis=0)
        P_val[p] = [int(pt) for pt in P_masks[p]]
        cnt = 0
        for i, val in enumerate(P_val[p]):
            if val == 1:
                P_val[p][i] = smp[cnt]
                cnt += 1
        P_val[p] = prev_scaler.inverse_transform(P_val[p])

    im = plt.imread('blank_game.png')
    implot = plt.imshow(im)
    choice = 50
    for p in P_val:
        if P_masks[p][0] == True:
            plt.scatter(P_val[p][0], 475, marker="s", s=120, alpha=0.5, edgecolors="none")
            plt.text(P_val[p][0] - 20, 475 + choice, p, fontsize=6)
            choice *= -1

    plt.show()
    plt.savefig('3_1_C.png', dpi=480)


def plot_kde(partitioned_options, prev_scaler, option):
    nsmp = 500
    P_val = {}
    for i in range(len(partitioned_options["move"][0].kde_models)):
        if partitioned_options["move"][0].nextOption[i][:-1] == option:
            kde = partitioned_options["move"][0].kde_models
            smp = kde[i].sample(nsmp)
            mask = np.zeros([nsmp, 33])
            for j in range(nsmp):
                mask[j][0] = smp[j]
            P_val[i] = prev_scaler.inverse_transform(mask)

    im = plt.imread('blank_game.png')
    implot = plt.imshow(im)
    colors = cm.rainbow(np.linspace(0, 1, len(P_val)))
    choice, count, shift = 55, 0, 0
    for p in P_val:
        # shift = -50
        next_option = partitioned_options["move"][0].nextOption[p][:-1]
        next_part = partitioned_options["move"][0].nextOption[p][-1]
        obj = [(o+1)/3 for o, val in enumerate(partitioned_options[next_option][int(next_part)].mask[0][3:])
               if val and (o+1)%3 == 0]
        y_idx = obj[0]
        if obj[0] >= 5:
            y_idx = len(P_val) - obj[0] + 1
            # shift = 50
        for k in P_val[p]:
            plt.scatter(k[0], 350 + (choice*y_idx), c=colors[count], marker="o", s=300, alpha=0.25, edgecolors="none")
        plt.text(np.mean(P_val[p], axis=0)[0]-50+shift, 360+(choice*y_idx), option+' '+str(obj[0]), fontsize=10, weight='bold')
        count += 1

    plt.show()
    plt.savefig('move'+option+'_kde.png', dpi=480)


# plot_symbols(the_scaler)
plot_kde(partitioned_options, the_scaler, 'place')

print "Done"
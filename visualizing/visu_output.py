import matplotlib.pyplot as plt
import pickle
import numpy as np
import tools
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV

# # add those lines to generator
# f = open('temp_output.p', 'wb')
# pickle.dump((P, P_masks), f)
# f.close()

all_samples = []
all_symbols = []
all_range = []
all_text = []
fig = None

def onclick(event):
    #print event.xdata, event.ydata
    all_dists = []
    for i in range(len(all_symbols)):
        #print i
        dist = tools.spherical(all_symbols[i][0], (event.xdata, event.ydata))
        all_dists.append(dist)
        if dist < 0.1:
            all_samples[i].set_alpha(0.05)
            all_range[i].set_alpha(0.5)
            all_text[i].set_alpha(1)
        else:
            all_samples[i].set_alpha(0)
            all_range[i].set_alpha(0)
            all_text[i].set_alpha(0)
    fig.canvas.draw()
    fig.canvas.flush_events()
    return

if __name__ == '__main__':
    f = open('fast_temp_output.p')
    (P, P_masks) = pickle.load(f)
    f.close()

    fig = plt.figure(figsize=(12, 9), dpi=90)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ax = fig.gca()
    ax.axis("equal")

    discard = []

    for i in P:
        samples = P[i].sample(1000)
        # the y axis is up-side-down
        if len(samples[0]) == 3:
            samples = samples * np.array([[1, -1, 1]])
        else:
            pass

        # objects, x, y, bool
        if len(samples[0]) >= 2:
            avg = np.average(samples, axis=0)
            ax.scatter(avg[0], avg[1], alpha=1)
            ax.scatter(avg[0], avg[1], alpha=1, marker='+', color='k', linewidths='1', s=160)
            r = tools.gaussian_r(samples)
            mask = P_masks[i]
            num_mask = []
            for j in range(len(mask)):
                if mask[j] == True :
                    num_mask.append(j)

            num_mask.sort()

            # pre-display all sample points, but invisible (alpha = 0).
            all_samples.append(ax.scatter(samples[:, 0], samples[:, 1], color='g', alpha=0))
            all_range.append(plt.Circle((avg[0:2]), radius=r, color='k', fill=False, alpha=0))
            ax.add_patch(all_range[-1])
            # display all symbols
            all_symbols.append(((avg[0], avg[1]), i, num_mask))

        # the player, x only or bool only
        else:
            r = tools.gaussian_r(samples)
            avg = np.average(samples)
            mask = P_masks[i]
            num_mask = []
            for j in range(len(mask)):
                if mask[j] == True :
                    num_mask.append(j)
            # bool case
            if 2 in num_mask:
                print 'discard symbol (player boolean): ' + str(i)
                continue
            ax.scatter(avg, -1.0, alpha=1)
            ax.scatter(avg, -1.0, alpha=1, marker='+', color='k', linewidths='1', s=160)

            all_samples.append(ax.scatter(samples[:, 0], [-1.0] * len(samples), color='g', alpha=0))
            all_range.append(plt.Rectangle((avg-r, -1.0-0.05), width=2*r, height=0.1, color='k', fill=False, alpha=0))
            ax.add_patch(all_range[-1])
            all_symbols.append(((avg, -1.0), i, num_mask))

    print all_symbols

    # put symbols with similar position together
    # what are those masks
    # group is a 2D list
    groups = [[0]]
    for i in range(1, len(all_symbols)):
        next = False
        for group in groups:
            for k in group:
                dist = tools.spherical(all_symbols[i][0], all_symbols[k][0])
                if dist < 0.1 and next == False:
                    group.append(i)
                    next = True

        if next == False:
            groups.append([i])
    print groups

    for i in range(len(all_symbols)):
        for group in groups:
            if i in group:
                mask = str(all_symbols[i][2])
                if len(group) > 1:
                    total = len(group)
                    pos = group.index(i)
                    all_text.append(ax.text(all_symbols[i][0][0] - 0.2, all_symbols[i][0][1] + 0.1 * (pos-total/2),
                                            'symbols: ' + all_symbols[i][1] + ' have masks ' + mask, alpha=0))
                    pass
                else:
                    all_text.append(ax.text(all_symbols[i][0][0]-0.2, all_symbols[i][0][1]+0.2, 'symbols: "' + all_symbols[i][1] + '" have masks ' + mask, alpha=0))

        #all_text.append(ax.text(, -1.0, str(num_mask)))

    #print all_symbols
    #fig.draw()
    plt.show()


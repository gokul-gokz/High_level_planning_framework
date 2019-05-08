
import pickle
import numpy as np
from os.path import dirname, abspath
import numpy as np
import definitions as d
from helpers import *
from sklearn.preprocessing import StandardScaler



root = dirname(dirname(dirname(abspath(__file__))))
partitioned_options = pickle.load(open(root + "/PPDDL_Generation/option_data.p", "rb"))


option_list = partitioned_options.keys()

all_s_by_partition = {}
for o in option_list:
    for i in range(len(partitioned_options[o])):
        all_s_by_partition[(o,i)] = merge_on_dim_3(partitioned_options[o][i].data, idx=0)


for o in option_list:
    for i in range(len(partitioned_options[o])):
        # order svm training data
        pos_data = all_s_by_partition[(o,i)]
        neg_data = [all_s_by_partition[key] for key in all_s_by_partition.keys() if key != (o,i)]
        neg_data = reduce(lambda x,y: x + y, neg_data, [])
        np.random.shuffle(neg_data)
        neg_data = neg_data[0:4000]
        labels = [0] * len(neg_data) + [1] * len(pos_data)
        init_svm_data = neg_data + pos_data

        # train magic models
        print o,i
        partitioned_options[o][i].fit_init(init_svm_data, labels)
        print "Completed training init sets"
        # partitioned_options[o][i].fit_KDEs()
        # print "Completed estimating Kernel Density for partition: " + str(i)
        # partitioned_options[o][i].fit_rewards()
        # print "Completed training reward model for partition: " + str(i)

print 'test'
root = dirname(dirname(dirname(abspath(__file__))))
pickle.dump(partitioned_options, open(root + "/PPDDL_Generation/option_data.p", "wb"))

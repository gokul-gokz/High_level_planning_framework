"""
This code takes data from records in format C and converts them to format B
-Max
"""


import os
import pickle
import numpy as np

def reorder_fucking_objects(records):
    first = records[0][0]
    xes = list(first[3::3])
    sortedx = sorted(xes)
    obj_order = [xes.index(i) for i in sortedx]
    new_records = []

    for sample in records:
        new_sample = list(sample)
        for k in [0,3]:
            # for i in obj_order
            new_s = [list(sample[k][0:3])] + [list(sample[k][3+3*i:6+3*i]) for i in obj_order]
            new_s = tuple([item for sublist in new_s for item in sublist])
            new_sample[k] = new_s
        new_records.append(tuple(new_sample))

    return new_records


all_records = os.listdir('Trial_Data')

allC = []
norm_C = []
fast_C = []
acc_C = []
for file in all_records:
       if file.endswith('C.p'):
            B_made = False
            if not file[:-3] + 'B.p' in all_records:
                B_made = False

            trials = pickle.load(open('Trial_Data/' + file, "rb"))
            C_trials = trials
            for key in trials.keys():
                records = trials[key][0]
                records = reorder_fucking_objects(records)
                new_records = []
                C_trials[key][0] = records


                for sample in records:
                    allC.append(sample)

                    if file.endswith('1_C.p'):
                        norm_C.append(sample)
                    elif file.endswith('2_C.p'):
                        fast_C.append(sample)
                    elif file.endswith('3_C.p'):
                        acc_C.append(sample)

                    new_sample = list(sample)
                    if B_made is False:
                        if True in sample[0]:
                            s = list(sample[0])
                            gripds = [i for i, x in enumerate(s) if x == True]    #two things would be true, the gloabl gripper and he grip for the object in hand
                            s[gripds[1] - 2] = s[0]
                            s[gripds[1] - 1] = s[1]
                            new_sample[0] = tuple(s)
                        if True in sample[3]:
                            s_p = list(sample[3])
                            gripds = [i for i, x in enumerate(s_p) if x == True]    #two things would be true, the gloabl gripper and he grip for the object in hand
                            s_p[gripds[1] - 2] = s_p[0]
                            s_p[gripds[1] - 1] = s_p[1]
                            new_sample[3] = tuple(s_p)
                        new_records.append(tuple(new_sample))
                    if B_made is False:
                        trials[key][0] = new_records



            f = open('Trial_Data/' + file[:-3] + 'B.p', 'w')
            pickle.dump(trials, f)
            f.close()
            f = open('Trial_Data/' + file, 'w')
            pickle.dump(C_trials, f)
            f.close()



f = open('Trial_Data/All_C_Records.p', 'w')
pickle.dump(allC, f)
f.close()
f = open('Trial_Data/All_Norm_C_Records.p', 'w')
pickle.dump(norm_C, f)
f.close()
f = open('Trial_Data/All_Fast_C_Records.p', 'w')
pickle.dump(fast_C, f)
f.close()
f = open('Trial_Data/All_Acc_C_Records.p', 'w')
pickle.dump(acc_C, f)
f.close()

allB = []
norm_B = []
fast_B = []
acc_B = []
for file in all_records:
    if file.endswith('B.p'):
        trials = pickle.load(open('Trial_Data/' + file, "rb"))
        for key in trials.keys():
            records = trials[key][0]
            for sample in records:
                allB.append(sample)

f = open('Trial_Data/All_B_Records.p', 'w')
pickle.dump(allB, f)
f.close()

print "done"


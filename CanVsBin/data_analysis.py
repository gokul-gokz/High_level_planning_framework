import matplotlib.pyplot as plt
import pickle
import numpy as np
from scipy.stats import mode
import os
import random
from copy import deepcopy

def time_click_analysis():
    time_data, click_data = [], []
    for i in range(24):
        f = open('Trial_Data/record'+str(i+1)+'_1_C.p')
        subject_data = pickle.load(f)
        total_time, total_clicks = 0, 0
        for j in range(len(subject_data)):
            total_time += subject_data[j][1]
            total_clicks += subject_data[j][2]
        norm_time = total_time / len(subject_data)
        norm_clicks = total_clicks / len(subject_data)
        f.close()
        f = open('Trial_Data/record' + str(i+1) + '_2_C.p')
        subject_data = pickle.load(f)
        total_time, total_clicks = 0, 0
        for j in range(len(subject_data)):
            total_time += subject_data[j][1]
            total_clicks += subject_data[j][2]
        fast_time = total_time / len(subject_data)
        fast_clicks = total_clicks / len(subject_data)
        f.close()
        f = open('Trial_Data/record' + str(i+1) + '_3_C.p')
        subject_data = pickle.load(f)
        total_time, total_clicks = 0, 0
        for j in range(len(subject_data)):
            total_time += subject_data[j][1]
            total_clicks += subject_data[j][2]
        acc_time = total_time / len(subject_data)
        acc_clicks = total_clicks / len(subject_data)
        f.close()
        if fast_time <= norm_time and fast_time <= acc_time:
            time_data.append([norm_time, fast_time, acc_time])
        if acc_clicks <= norm_clicks and acc_clicks <= fast_clicks:
            click_data.append([norm_clicks, fast_clicks, acc_clicks])
    mean_time = np.mean(time_data, axis=0)
    std_time = np.std(time_data, axis=0)
    mean_click = np.mean(click_data, axis=0)

    time_diff, time_diff_perc = [], []
    for i in time_data:
        time_diff.append([i[0]-i[1], i[1]-i[2], i[2]-i[0]])
        time_diff_perc.append([(i[0]-i[1])/i[0], (i[1]-i[2])/i[1], (i[2]-i[0])/i[0]])
    mean_time_diff = np.mean(time_diff, axis=0)
    mean_time_diff_perc = np.mean(time_diff_perc, axis=0)

    mode_time_diff = mode(np.round(time_diff, 1))
    mode_time_diff_perc = mode(np.round(time_diff_perc, 2))

    return mean_time, std_time, mean_click, mean_time_diff, mean_time_diff_perc, mode_time_diff, mode_time_diff_perc

def get_plan(data):
    temp_plan, moves, cost = [], 0, 0
    for k in data:
        if k[1] == 'pick':
            obj = [str(((l+1)/3) - 1) for l in range(5, len(k[3]), 3) if k[3][l]]
            temp_plan.append(k[1] + obj[0])
        elif k[1] == 'place':
            obj = [str(((l+1)/3) -1) for l in range(5, len(k[0]), 3) if k[0][l]]
            temp_plan.append(k[1] + obj[0])
        else:
            obj = ['']
            moves += 1
            cost += k[2]
        # temp_plan.append(k[1]+obj[0])

    return temp_plan, moves, cost



def plan_analysis(cond):
    plan, moves, cost = [], [], []
    for i in range(24):
        f = open('Trial_Data/record'+str(i+1)+'_' + str(cond)+'_C.p')
        subject_data = pickle.load(f)
        cond_plan, cond_moves, cond_cost = [], [], []
        for j in subject_data:
            trial_plan, trial_moves, trial_cost = get_plan(subject_data[j][0])
            cond_plan.append(str(trial_plan))
            cond_moves.append(trial_moves)
            cond_cost.append(trial_cost)
        plan.append(cond_plan)
        moves.append(cond_moves)
        cost.append(cond_cost)

    return plan, moves, cost

# -------------------------------------------------------------------------------------------------------------------- #


norm_plan, norm_moves, norm_cost = plan_analysis(1)
fast_plan, fast_moves, fast_cost = plan_analysis(2)
acc_plan, acc_moves, acc_cost = plan_analysis(3)

mode_norm, mode_fast, mode_acc = [], [], []
for i in range(len(norm_plan)):
    mode_norm.append(mode(norm_plan[i])[0][0])
    mode_fast.append(mode(fast_plan[i])[0][0])
    mode_acc.append(mode(acc_plan[i])[0][0])
NormPlan = mode(mode_norm)[0][0]
FastPlan = mode(mode_fast)[0][0]
AccPlan = mode(mode_acc)[0][0]

FastMoves = np.mean(fast_moves, axis=1)
AccMoves = np.mean(acc_moves, axis=1)
FastCost = np.mean(fast_cost, axis=1)
AccCost = np.mean(acc_cost, axis=1)

MovesPerc, CostPerc = [], []
for i in range(len(FastMoves)):
    MovesPerc.append(100*(FastMoves[i]-AccMoves[i])/FastMoves[i])
    CostPerc.append(100 * (AccCost[i] - FastCost[i]) / AccCost[i])
MeanMovesPerc = np.mean(MovesPerc)
MeanCostPerc = np.mean(CostPerc)

print "Done"
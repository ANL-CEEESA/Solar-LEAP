import PySimpleGUI as sg

import matplotlib
matplotlib.use("Agg")  # Set backend to Agg to prevent figure from appearing as a separate window
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import math
from scipy.stats import weibull_min
import textwrap
import random

from tqdm import tqdm
import warnings
import logging
import os


random.seed(10)

def dist_prep(input_scale_dict, inv_num, day_it_inv, ft_sample_inv):
    input_scale = input_scale_dict [f'i{inv_num}']
    shape1 = 4  # Shape parameter (you can adjust this)
    scale1 = input_scale
    # mean1 = scale1 * ((np.pi / 2) ** (1 / shape1))
    # mean_current = mean1 - day_it_inv
    # scale1 = mean_current / (np.pi / 2) ** (1 / shape1)

    # Generate data points, to be updated by Liming's pdf and cdf
    x_values = np.linspace(0, weibull_min.ppf(0.999, shape1, scale=scale1), 200)
    # y_pdf_values = weibull_min.pdf(x_values, shape1, scale=scale1)
    # y_cdf_values = weibull_min.cdf(x_values, shape1, scale=scale1)

    y_pdf_values = weibull_min.pdf(x_values + day_it_inv, shape1, scale=scale1) / (1 - weibull_min.cdf(day_it_inv, shape1, scale=scale1))
    y_cdf_values = (weibull_min.cdf(x_values + day_it_inv, shape1, scale=scale1) - weibull_min.cdf(day_it_inv, shape1, scale=scale1)) / (1 - weibull_min.cdf(day_it_inv, shape1, scale=scale1))

    if day_it_inv == 0:
        while True:
            ft_sample_inv = math.ceil(input_scale_dict ['i2'] * np.random.weibull(4))        # failure time is always the real EUR
            if ft_sample_inv >= 200:
                break
        # make sure it is larger than step_days = 100 or 50

    distance_ft = ft_sample_inv - day_it_inv

    return [x_values, y_pdf_values, y_cdf_values, ft_sample_inv, distance_ft]

def dmc_prep(inv_num, x_values, day_it_inv, input_c_f, input_c_p, y_cdf_values, distance_ft):
    Dynamic_maintenance_cost_list = []  # for all periods, we will calculate the dynamic maintenance costs


    x_indices = range(1, len(x_values))
    # One is observation time and the other one is "t" time periods after the observation.
    c_f = input_c_f
    c_p = input_c_p

    # for x in x_indices:  # Maintenance time C_x
    #     numerator = c_p * (1 - y_cdf_values[x]) + c_f * y_cdf_values[x]
    #     denominator = day_it_inv  # could be set to zero as well can try both
    #     for y in x_indices:
    #         if y<=x:
    #             denominator += (1 - y_cdf_values[y])
    #
    #     func_value = numerator / denominator

    for x in x_indices:  # Maintenance time C_x
        func_value = 0
        for x_2 in x_indices:  # failure time
            if x_2 <= x:  # If it fails before the maintenance time--> conduct corrective maintenance
                if x_2 == 1:
                    func_value += (x - x_2) * c_f * y_cdf_values[x_2 - 1]
                else:

                    func_value += (x - x_2) * c_f * (y_cdf_values[x_2 - 1] - y_cdf_values[x_2 - 2])
            else:  # x<x_2#If it maintains before failure time, preventive maintenance
                func_value += (x_2 - x) * c_p * (y_cdf_values[x_2 - 1] - y_cdf_values[x_2 - 2])

        Dynamic_maintenance_cost_list.append(func_value)
    min_idx_maint_day = np.argmin(Dynamic_maintenance_cost_list) + 1
    min_cost_maint_day = math.floor(x_values[min_idx_maint_day])
    min_cost_maint_cost = Dynamic_maintenance_cost_list[min_idx_maint_day]

    if inv_num == 1:
        distance_mt = min_cost_maint_day - 201
    elif inv_num == 2:
        distance_mt = min_cost_maint_day - 301
    # proposed should be better?
    # mt2 = min_cost_maint_day - simulation_step_days
    # mt2_distance = mt2 - day_it

    # find out if straight line should be dotted or not.
    ft_line_flag = 0
    if distance_mt > distance_ft:  # corrective maintenance after failure
        ft_line_flag = 1

    return [distance_mt, ft_line_flag, Dynamic_maintenance_cost_list, min_cost_maint_day, min_cost_maint_cost]

# 365*30 = 10950
# choose 11000 days, 100 days a step, that's 110 steps.


def inv_simulation (inv_num, input_scale_dict, input_c_p, input_c_f, na_days_pm, na_days_cm, simulation_end_days, simulation_step_days, day, day_it,
                    maint_day, maint_type, maint_na_days, maint_cost, ft_sample):

    # test - could use this to aim for good results
    # random.seed(10)

    # logger.info(f'Inverter - Started Simulation for {simulation_end_days} days')


    # input_scale = input_scale_dict [f'i{inv_num}']
    day_it_inv = day_it[f'i{inv_num}']
    ft_sample_inv = ft_sample[f'i{inv_num}']

    # stage 1 - distribution
    [x_values, y_pdf_values, y_cdf_values, ft_sample_inv, distance_ft] = dist_prep(input_scale_dict, inv_num, day_it_inv, ft_sample_inv)
    # stage 2 - dynamic maintenance cost
    [distance_mt, ft_line_flag, Dynamic_maintenance_cost_list, min_cost_maint_day, min_cost_maint_cost] = dmc_prep (inv_num, x_values, day_it_inv, input_c_f, input_c_p, y_cdf_values, distance_ft)



    if (distance_mt <= 0 or distance_ft <= 0):
        if distance_mt <= distance_ft: # preventive maintenance before failure
            maint_day[f'i{inv_num}'].append(day + distance_mt)
            maint_type[f'i{inv_num}'].append('PM')
            maint_na_days[f'i{inv_num}'] += na_days_pm
            maint_cost[f'i{inv_num}'] += input_c_p
        else:                           # corrective maintenance after failure
            maint_day[f'i{inv_num}'].append(day + distance_ft)
            maint_type[f'i{inv_num}'].append('CM')
            maint_na_days[f'i{inv_num}'] += na_days_cm + math.ceil((random.random()-0.5) * 10)
            maint_cost[f'i{inv_num}'] += input_c_f
        day_it_inv = 0

        [x_values, y_pdf_values, y_cdf_values, ft_sample_inv, distance_ft] = dist_prep(input_scale_dict, inv_num, day_it_inv, ft_sample_inv)
        [distance_mt, ft_line_flag, Dynamic_maintenance_cost_list, min_cost_maint_day, min_cost_maint_cost] = dmc_prep (inv_num, x_values, day_it_inv, input_c_f, input_c_p, y_cdf_values, distance_ft)



    # process the table of maintenance history and table of maint. summary
    tab_history_cell_text = []
    tab_history_cell_color = []
    tab_summary_pm_count = 0
    tab_summary_cm_count = 0
    if len(maint_day[f'i{inv_num}']) != 0:
        for maint_day_idx in range(len(maint_day[f'i{inv_num}'])):
            cell_text_it = [maint_day[f'i{inv_num}'][maint_day_idx], maint_type[f'i{inv_num}'][maint_day_idx]]
            tab_history_cell_text.append(cell_text_it)

            if maint_type[f'i{inv_num}'][maint_day_idx] == 'PM':
                tab_history_cell_color.append(['w', 'g'])
                tab_summary_pm_count += 1
            elif maint_type[f'i{inv_num}'][maint_day_idx] == 'CM':
                tab_history_cell_color.append(['w', 'r'])
                tab_summary_cm_count += 1
    maint_na_days_inv = maint_na_days[f'i{inv_num}']
    maint_cost_inv = maint_cost[f'i{inv_num}']
    if day != 0:
        tab_summary_cell_text = [['# of PM', tab_summary_pm_count],
                                 ['# of CM', tab_summary_cm_count],
                                 ['N/A Days', f'{round(maint_na_days_inv/(day/365), 2)}/yr'],
                                 ['Maint. Cost', f'${round(maint_cost_inv * (11/(18*6000/60)) / ((day/365)) , 2)}/kW-yr']]
        # aim to put the benchmark to $11/kW-yr, so each year per unit base is 18 CM in 60 yrs average to per year multiply by $11
    else:
        tab_summary_cell_text = [['# of PM', tab_summary_pm_count],
                                 ['# of CM', tab_summary_cm_count],
                                 ['N/A Days', f'0/yr'],
                                 ['Maint. Cost', f'$ 0/kW-yr']]
    # TODO: 60000 needs to be verified on 0.0148 for multiple simulation times


    # logger.info(f'Inverter - Completed Simulation for {simulation_end_days} days')
    ft_sample[f'i{inv_num}'] = ft_sample_inv
    day_it[f'i{inv_num}'] = day_it_inv
    return [x_values, y_pdf_values, distance_ft, ft_line_flag, Dynamic_maintenance_cost_list, min_cost_maint_day, min_cost_maint_cost, tab_history_cell_text, tab_history_cell_color, tab_summary_cell_text], [maint_day, maint_type, maint_na_days, maint_cost, ft_sample, day_it]



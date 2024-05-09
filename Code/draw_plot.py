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



def draw_plot_f1(inv_num, canvas_fig_ax_dict, day, day_it, plot_data):

    # Clear previous drawing
    canvas_fig_ax_dict[f'ax_i{inv_num}_f1'].clear()

    x_values = plot_data[f'i{inv_num}'][0]
    y_pdf_values = plot_data[f'i{inv_num}'][1]
    distance_ft = plot_data[f'i{inv_num}'][2]
    ft_line_flag = plot_data[f'i{inv_num}'][3]


    # canvas_fig_ax_dict [f'fig_i{inv_num}_f1'], canvas_fig_ax_dict [f'ax_i{inv_num}_f1'] = plt.subplots(figsize=figsize)

    if inv_num == 1:
        canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].plot(x_values, y_pdf_values, 'r-', lw=1, label='BENCHMARK: w/o consideration of EUR')
    elif inv_num ==2:
        canvas_fig_ax_dict[f'ax_i{inv_num}_f1'].plot(x_values, y_pdf_values, 'g-', lw=1, label='PROPOSED: w/ consideration of EUR')

    if ft_line_flag == 0:
        canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].plot([distance_ft, distance_ft], [0, max(y_pdf_values) * 1.05], 'k--', lw=2, label='actual failure time')
    elif ft_line_flag == 1:
        canvas_fig_ax_dict[f'ax_i{inv_num}_f1'].plot([distance_ft, distance_ft], [0, max(y_pdf_values) * 1.05], 'k-',lw=2, label='actual failure time')

    canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].set_title(f'Failure Time Distribution at Day {day}')
    canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].set_xlabel('Time in Days')
    canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].set_ylabel('Probability Density')
    canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].set_ylim(0, 0.0018)
    canvas_fig_ax_dict[f'ax_i{inv_num}_f1'].set_xlim(right=4000)
    canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].legend()
    canvas_fig_ax_dict [f'ax_i{inv_num}_f1'].grid(True)

    canvas_fig_ax_dict [f'fig_i{inv_num}_f1'].tight_layout()
    # Close the figure to free up memory
    plt.close(canvas_fig_ax_dict [f'fig_i{inv_num}_f1'])
    # Update canvas
    canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f1'].draw()

    # current_index_inv1 = (current_index_inv1 + 1) % INV_fig1_count

def draw_plot_f2(inv_num, canvas_fig_ax_dict, day, day_it, plot_data):

    # Clear previous drawing
    canvas_fig_ax_dict[f'ax_i{inv_num}_f2'].clear()

    x_values = plot_data[f'i{inv_num}'][0]
    Dynamic_maintenance_cost_list = plot_data[f'i{inv_num}'][4]
    min_cost_maint_day = plot_data[f'i{inv_num}'][5]
    min_cost_maint_cost = plot_data[f'i{inv_num}'][6]
    ft_line_flag = plot_data[f'i{inv_num}'][3]

    # fig_2, ax_2 = plt.subplots(figsize = figsize)



    if inv_num == 1:
        canvas_fig_ax_dict [f'ax_i{inv_num}_f2'].plot(x_values[1:], Dynamic_maintenance_cost_list, 'r-', lw=1, label='BENCHMARK: w/o consideration of EUR')
    elif inv_num ==2:
        canvas_fig_ax_dict[f'ax_i{inv_num}_f2'].plot(x_values[1:], Dynamic_maintenance_cost_list, 'g-', lw=1, label='PROPOSED: w/ consideration of EUR')
    if ft_line_flag == 0:
        canvas_fig_ax_dict [f'ax_i{inv_num}_f2'].plot([min_cost_maint_day, min_cost_maint_day], [0, min_cost_maint_cost*1.05], 'k-', lw=2, label = 'suggested maint. time')
    elif ft_line_flag == 1:
        canvas_fig_ax_dict[f'ax_i{inv_num}_f2'].plot([min_cost_maint_day, min_cost_maint_day], [0, min_cost_maint_cost * 1.05], 'k--', lw=2, label='suggested maint. time')

    canvas_fig_ax_dict [f'ax_i{inv_num}_f2'].set_title(f'Dynamic Maintenance Cost at Day {day}')
    canvas_fig_ax_dict [f'ax_i{inv_num}_f2'].set_xlabel('Time in Days')
    canvas_fig_ax_dict [f'ax_i{inv_num}_f2'].set_ylabel('Maintenance Cost')
    canvas_fig_ax_dict[f'ax_i{inv_num}_f2'].set_ylim(top=500000)
    canvas_fig_ax_dict[f'ax_i{inv_num}_f2'].set_xlim(right=4000)
    canvas_fig_ax_dict [f'ax_i{inv_num}_f2'].legend()
    canvas_fig_ax_dict [f'ax_i{inv_num}_f2'].grid(True)

    canvas_fig_ax_dict [f'fig_i{inv_num}_f2'].tight_layout()

    # Close the figure to free up memory
    plt.close(canvas_fig_ax_dict [f'fig_i{inv_num}_f2'])
    # Update canvas
    canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f2'].draw()

def draw_plot_f3 (inv_num, canvas_fig_ax_dict, day, day_it, plot_data, maint_na_days, maint_cost, eur_proposed):

    # Clear previous drawing
    canvas_fig_ax_dict [f'ax_i{inv_num}_f3'][0].clear()
    canvas_fig_ax_dict[f'ax_i{inv_num}_f3'][1].clear()

    canvas_fig_ax_dict[f'ax_i{inv_num}_f3'][0].axis('off')
    canvas_fig_ax_dict[f'ax_i{inv_num}_f3'][1].axis('off')

    tab_history_cell_text = plot_data[f'i{inv_num}'][7]
    tab_history_cell_color = plot_data[f'i{inv_num}'][8]
    tab_summary_cell_text1 = plot_data[f'i{inv_num}'][9]
    tab_summary_cell_text2 = tab_summary_cell_text1

    tab_summary_cell_color1 = [['w', 'g'], ['w', 'r'], ['w', 'w'], ['w', 'w']]
    tab_summary_cell_color2 = tab_summary_cell_color1

    if (maint_na_days [f'i1'] != 0 and maint_na_days [f'i2'] != 0):
        na_reduct_per = (maint_na_days [f'i2'] - maint_na_days [f'i1'])  / maint_na_days [f'i1']
        na_reduct_per = round (-na_reduct_per*100, 1)
        cost_reduct_per = (maint_cost[f'i2'] - maint_cost[f'i1'])  / maint_cost[f'i1']
        cost_reduct_per = round(-cost_reduct_per*100, 1)
        tab_summary_cell_text2 = tab_summary_cell_text1 + [['N/A Reduction', f'{na_reduct_per}%'], ['Cost Reduction', f'{cost_reduct_per}%']]

        tab_summary_cell_color2 = tab_summary_cell_color1 + [['w', 'g'], ['w', 'g']]



    # plot the table of maintenance history
    # fig_3, (ax_3, ax_4) = plt.subplots(1,2,figsize=(6, 4))

        canvas_fig_ax_dict [f'ax_i{inv_num}_f3'][0].axis('off')
        tab_history = canvas_fig_ax_dict [f'ax_i{inv_num}_f3'][0].table(cellText=tab_history_cell_text,
                                                                        cellColours = tab_history_cell_color,
                                                                        cellLoc = 'center',
                                                                        colLabels=['Day', 'Maint.'],
                                                                        loc='center',
                                                                        colLoc='center')
        canvas_fig_ax_dict [f'ax_i{inv_num}_f3'][0].set_title(f"Maint. Actions EUR = {eur_proposed}")

        canvas_fig_ax_dict [f'ax_i{inv_num}_f3'][1].axis('off')
        if inv_num == 1:
            table_summary = canvas_fig_ax_dict [f'ax_i{inv_num}_f3'][1].table(cellText=tab_summary_cell_text1,
                                                                              cellColours = tab_summary_cell_color1,
                                                                              cellLoc = 'center',
                                                                              loc='center',
                                                                              colLoc='center')
        elif inv_num ==2:  # proposed table add two rows as comparison
            table_summary = canvas_fig_ax_dict[f'ax_i{inv_num}_f3'][1].table(cellText=tab_summary_cell_text2,
                                                                             cellColours=tab_summary_cell_color2,
                                                                             cellLoc='center',
                                                                             loc='center',
                                                                             colLoc='center')
        canvas_fig_ax_dict [f'ax_i{inv_num}_f3'][1].set_title(f"Maint. Metrics until Day {day}")

        # Close the figure to free up memory
        plt.close(canvas_fig_ax_dict [f'fig_i{inv_num}_f3'])
        # Update canvas
        canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f3'].draw()



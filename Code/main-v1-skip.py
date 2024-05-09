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


# Create the folder for saving the figures
folder_name = 'figure_results_save'
folder_path = os.path.join(os.getcwd(), folder_name)

if not os.path.exists(folder_path):
    os.makedirs(folder_name)

logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
'''
# logging level
# logger.debug('Here you have some information for debugging.')
# logger.info('Everything is normal. Relax!')
# logger.warning('Something unexpected but not important happend.')
# logger.error('Something unexpected and important happened.')
# logger.critical('OMG!!! A critical error happend and the code cannot run!')
'''
# our first handler is a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler_format = '%(asctime)s | %(levelname)s: %(message)s'
console_handler.setFormatter(logging.Formatter(console_handler_format))
logger.addHandler(console_handler)

# the second handler is a file handler
file_handler = logging.FileHandler('Log_GUI.log')
file_handler.setLevel(logging.DEBUG)
file_handler_format = '%(asctime)s | %(levelname)s | %(lineno)d: %(message)s'
file_handler.setFormatter(logging.Formatter(file_handler_format))
logger.addHandler(file_handler)


EUR_record = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.0148]
scale_record = [2667.491938616467, 2523.0164743152513, 2378.541010014036, 2234.0655457128205, 2089.590081411605, 1945.1146171103892, 1800.6391528091735, 1656.163688507958, 1511.6882242067425, 1367.212759905527, 2598.1437157518835]
weibull_dict = dict(zip(EUR_record, scale_record))

from inv_simulation import inv_simulation, dist_prep, dmc_prep
from draw_plot import draw_plot_f1, draw_plot_f2, draw_plot_f3



# Choose a Theme for the Layout
# sg.theme('DefaultNoMoreNagging')
sg.theme('Python')
# sg.set_options(scaling=0.8)

# Define the layout of the GUI

NAME_SIZE = 30
def name(name):
    dots = NAME_SIZE-len(name)+10
    return sg.Text(name + ' ' + ' '*dots, size=(NAME_SIZE,1), justification='l',pad=(0,0), font=('Helvetica', 10))

# Define the list of preventive cost
preventive_maintenance_cost_list = [1500, 3000, 4500, 6000, 7500, 9000]
corrective_maintenance_cost_list = [1500, 3000, 4500, 6000, 7500, 9000]

figsize = (6, 4)
inv_title_size = 12
slider_size = (14, 15)  # (width, height)



# Create the first window
while True:

    # Define the layout for the first window
    layout1 = [
        [sg.Push(), sg.Text('Prognostic Module for Solar Inverters - Input', font=('Helvetica', 24), justification='c', expand_x=True), sg.Push()],
        [sg.HSep()],
        [sg.Push(), sg.Text('Scenario Setup', font=("Helvetica", 18, "bold")), sg.Push()],
        [name('EUR (Equivalent Under-sizing Rate)'), sg.Slider(range=(.01, .1), resolution=.01, default_value=10, orientation='h', s=slider_size, disable_number_display = False, key="-drift_inv1-")],
        [name('Preventive Maintenance Cost ($)'), sg.Combo(preventive_maintenance_cost_list, default_value=preventive_maintenance_cost_list[0], s=(15, 20), enable_events=False, readonly=True, k='-pmc_inv1-')],
        [name('Corrective Maintenance Cost ($)'), sg.Combo(corrective_maintenance_cost_list, default_value=corrective_maintenance_cost_list[3], s=(15, 20), enable_events=False, readonly=True, k='-cmc_inv1-')],
        [sg.HSep()],
        [sg.Image(filename='./window1-failure-time.png', size=(800, 500), key="-w1_ft-")],
        [sg.HSep()],

        [sg.Push(), sg.Button("Start Simulation", size=(30, 2), key="-window_next-"), sg.Push()],

        [sg.Push(), sg.Button("Start Simulation (skip visualization)", size=(30, 2), key="-window_skip-"), sg.Push()],

        [sg.Sizer(1, 40)],
        [sg.HSep()],
        [sg.Text(
            'This tool is based upon work supported by the U.S. Department of Energy',
            font=('Helvetica', 10), justification='r', expand_x=True)],
        [sg.Text(
            'Office of Energy Efficiency and Renewable Energy (EERE)',
            font=('Helvetica', 10), justification='r', expand_x=True)],
        [sg.Text(
            'under the Solar Energy Technologies Office Award Number 39640.',
            font=('Helvetica', 10), justification='r', expand_x=True)],
    ]

    window1 = sg.Window('Prognostic Module for Solar Inverters - Input', layout1, resizable=True)

    # event1, values1 = window1.read(timeout=1000)
    event1, values1 = window1.read()

    # If the "Open Window B" button is clicked, close the first window and open the second window
    if event1 == '-window_next-':
        # window1.close()       # KEEP window1 open, so that the input can be compared with output

        # use a while loop to keep trying the function call until no RuntimeWarning is raised.
        while True:
            with warnings.catch_warnings():
                warnings.simplefilter("error", RuntimeWarning)
                try:
                    # parameter preset before start of simulations
                    na_days_pm = 1
                    na_days_cm = 65
                    simulation_end_days = 100 * 219
                    simulation_step_days = 100
                    simulation_step_len = simulation_end_days / simulation_step_days
                    eur_population = 0.0148
                    # parameter preset before start of simulations
                    inv_num_range = range(1, 3)
                    day = 0

                    plot_data = {}
                    day_it = {}
                    for inv_num in inv_num_range:
                        day_it[f'i{inv_num}'] = 0
                        plot_data[f'i{inv_num}'] = []

                    # specific for almost global variables
                    maint_day = {}
                    maint_type = {}
                    maint_na_days = {}
                    maint_cost = {}
                    ft_sample = {}
                    for inv_num in inv_num_range:
                        maint_day[f'i{inv_num}'] = []
                        maint_type[f'i{inv_num}'] = []
                        maint_na_days[f'i{inv_num}'] = 0
                        maint_cost[f'i{inv_num}'] = 0
                        ft_sample[f'i{inv_num}'] = 2100

                    # parameter preset before start of simulation in window2
                    eur_proposed = values1['-drift_inv1-']
                    input_eur = {'i1': eur_population, 'i2': eur_proposed}
                    input_scale_dict = {}
                    for inv_num in inv_num_range:
                        input_scale_dict [f'i{inv_num}'] = weibull_dict [input_eur [f'i{inv_num}']]
                    input_c_p = values1['-pmc_inv1-']
                    input_c_f = values1['-cmc_inv1-']

                    '''
                    # test code
                    eur_proposed = 0.1
                    input_c_p = 1500
                    input_c_f = 6000
                    '''

                    break  # Exit the loop if no warning is raised

                except RuntimeWarning as e:
                    logger.info(f'Caught a RuntimeWarning: {e}, re-start the simulation. ')
                    continue  # Continue to the next iteration if warning is raised

        # Initialize looping control variables
        looping = False


        # Define the layout for the second window
        layout2 = [
            [sg.Push(), sg.Text('Prognostic Module for Solar Inverters - Output (Comparison of O&M Framework)', font=('Helvetica', 18), justification='c', expand_x=True), sg.Push()],
            [sg.Push(), sg.Text(f'SAME EUR (Inverter Equivalent Under-sizing Rate) = {eur_proposed}', font=('Helvetica', 16), justification='c', expand_x=True), sg.Push()],
            [sg.HSep()],
            # [sg.Push(), sg.Text('Inverter 1', font=("Helvetica", inv_title_size, "bold")), sg.Push()],
            [sg.Col([[sg.Text('BENCHMARK', font=("Helvetica", inv_title_size, "bold"), size = (11,1))]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv1_fig1-")]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv1_fig2-")]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv1_fig3-")]], p=0)],
            [sg.HSep()],
            # [sg.Push(), sg.Text('Inverter 2', font=("Helvetica", inv_title_size, "bold")), sg.Push()],
            [sg.Col([[sg.Text('PROPOSED', font=("Helvetica", inv_title_size, "bold"), size = (11,1))]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv2_fig1-")]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv2_fig2-")]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv2_fig3-")]], p=0)],
            [sg.HSep()],
            # [sg.Push(), sg.Text('Inverter 3', font=("Helvetica", inv_title_size, "bold")), sg.Push()],
            # [sg.Col([[sg.Text('Inverter 3', font=("Helvetica", inv_title_size, "bold"))]], p=0), sg.VSep(),
            #  sg.Col([[sg.Image(filename=I3_fig1[0], size=image_size, key="-inv3_fig1-")]], p=0), sg.VSep(),
            #  sg.Col([[sg.Image(filename=I3_fig2[0], size=image_size, key="-inv3_fig2-")]], p=0), sg.VSep(),
            #  sg.Col([[sg.Image(filename=I3_fig3[0], size=image_size, key="-inv3_fig3-")]], p=0)],
            # [sg.HSep()],

            [sg.Push(), sg.Button("Start/Stop", size = (30,2), key="-STARTSTOP-"), sg.Push()],

            # [sg.Sizer(1, 40)],
            [sg.HSep()],
            [sg.Text(
                'This tool is based upon work supported by the U.S. Department of Energy Office of Energy Efficiency and Renewable Energy (EERE) under the Solar Energy Technologies Office Award Number 39640.',
                font=('Helvetica', 10), justification='r', expand_x=True)],
        ]

        window2 = sg.Window('Prognostic Module for Solar Inverters - Output', layout2, resizable=True, finalize=True)

        # Initialize the canvas and figure
        canvas_fig_ax_dict = {}
        for inv_num in inv_num_range:
            for canvas_num in range (1,4):
                canvas_fig_ax_dict [f'canvas_i{inv_num}_f{canvas_num}'] = window2[f'-inv{inv_num}_fig{canvas_num}-'].TKCanvas
                if canvas_num <= 2:
                    canvas_fig_ax_dict [f'fig_i{inv_num}_f{canvas_num}'] , canvas_fig_ax_dict [f'ax_i{inv_num}_f{canvas_num}'] = plt.subplots(figsize=figsize)
                else:
                    canvas_fig_ax_dict[f'fig_i{inv_num}_f{canvas_num}'], canvas_fig_ax_dict[f'ax_i{inv_num}_f{canvas_num}'] = plt.subplots(1,2,figsize=figsize)
                canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f{canvas_num}'] = FigureCanvasTkAgg(canvas_fig_ax_dict[f'fig_i{inv_num}_f{canvas_num}'], master=canvas_fig_ax_dict[f'canvas_i{inv_num}_f{canvas_num}'])
                canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f{canvas_num}'].draw()
                canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f{canvas_num}'].get_tk_widget().pack(side="top", fill="both", expand=True)


        while True:
            event2, values2 = window2.read(timeout=0)
            # event2, values2 = window2.read()

            # If the second window is closed, exit the program
            if event2 == sg.WINDOW_CLOSED:
                window1.close()
                window2.close()
                break


            if event2 == "-STARTSTOP-":
                if not looping:
                    window2['-STARTSTOP-'].update('Stop')
                    looping = True
                else:
                    window2['-STARTSTOP-'].update('Start')
                    looping = False

            if looping:
                try:  # Update the image to the next one in the list
                    # logger.info(f'started day {day}')
                    for inv_num in inv_num_range:
                        '''
                        # test code
                        inv_num = 1
                        '''

                        plot_data [f'i{inv_num}'], [maint_day, maint_type, maint_na_days, maint_cost, ft_sample, day_it] = inv_simulation (inv_num, input_scale_dict, input_c_p, input_c_f, na_days_pm, na_days_cm, simulation_end_days, simulation_step_days, day, day_it,
                                                                                                                                           maint_day, maint_type, maint_na_days, maint_cost, ft_sample)

                        # logger.info(f'completed day {day} - inv {inv_num} - simulation')

                        # almost global variables
                        # maint_day[f'i{inv_num}'] = plot_data [f'i{inv_num}'][10][f'i{inv_num}']
                        # maint_type[f'i{inv_num}'] = plot_data [f'i{inv_num}'][11][f'i{inv_num}']
                        # maint_na_days[f'i{inv_num}'] = plot_data [f'i{inv_num}'][12][f'i{inv_num}']
                        # maint_cost[f'i{inv_num}'] = plot_data [f'i{inv_num}'][13][f'i{inv_num}']
                        # ft_sample[f'i{inv_num}'] = plot_data [f'i{inv_num}'][14][f'i{inv_num}']

                        draw_plot_f1(inv_num, canvas_fig_ax_dict, day, day_it, plot_data)
                        # logger.info(f'completed day {day} - inv {inv_num} - fig1')
                        draw_plot_f2(inv_num, canvas_fig_ax_dict, day, day_it, plot_data)
                        draw_plot_f3(inv_num, canvas_fig_ax_dict, day, day_it, plot_data, maint_na_days, maint_cost, eur_proposed)

                    if day == simulation_end_days:
                        looping = False
                        window2['-STARTSTOP-'].update('Start')

                        # specific for almost global variables
                        maint_day = {}
                        maint_type = {}
                        maint_na_days = {}
                        maint_cost = {}
                        ft_sample = {}
                        for inv_num in inv_num_range:
                            maint_day[f'i{inv_num}'] = []
                            maint_type[f'i{inv_num}'] = []
                            maint_na_days[f'i{inv_num}'] = 0
                            maint_cost[f'i{inv_num}'] = 0
                            ft_sample[f'i{inv_num}'] = 2100

                        import time
                        timestr = time.strftime("%Y%m%d-%H%M%S")

                        day = 0
                        for inv_num in inv_num_range:
                            day_it[f'i{inv_num}'] = 0

                            canvas_fig_ax_dict[f'fig_i{inv_num}_f3'].savefig(
                                f'./figure_results_save/VIS_eur_{eur_proposed}_time_' + timestr + f'_inv_{inv_num}.png')





                    else:
                        day = day + simulation_step_days
                        for inv_num in inv_num_range:
                            day_it[f'i{inv_num}'] = day_it[f'i{inv_num}'] + simulation_step_days
                        # day_it[f'i{inv_num}'] = (day_it[f'i{inv_num}'] + 1) % simulation_step_len  # Wrap around to the start if we've reached the end


                except Exception as Argument:
                    logging.exception("Error in window 2 operation")

                    sg.popup_error('Something is not Correct, Exiting...')
                    window2['-STARTSTOP-'].update('Start')
                    looping = False

            # time.sleep(0.1)  # Wait for a short period to avoid using too much CPU time

    if event1 == '-window_skip-':
        # window1.close()       # KEEP window1 open, so that the input can be compared with output

        # use a while loop to keep trying the function call until no RuntimeWarning is raised.
        while True:
            with warnings.catch_warnings():
                warnings.simplefilter("error", RuntimeWarning)
                try:
                    # parameter preset before start of simulations
                    na_days_pm = 1
                    na_days_cm = 65
                    simulation_end_days = 100 * 219
                    simulation_step_days = 100
                    simulation_step_len = simulation_end_days / simulation_step_days
                    eur_population = 0.0148
                    # parameter preset before start of simulations
                    inv_num_range = range(1, 3)
                    day = 0

                    plot_data = {}
                    day_it = {}
                    for inv_num in inv_num_range:
                        day_it[f'i{inv_num}'] = 0
                        plot_data[f'i{inv_num}'] = []

                    # specific for almost global variables
                    maint_day = {}
                    maint_type = {}
                    maint_na_days = {}
                    maint_cost = {}
                    ft_sample = {}
                    for inv_num in inv_num_range:
                        maint_day[f'i{inv_num}'] = []
                        maint_type[f'i{inv_num}'] = []
                        maint_na_days[f'i{inv_num}'] = 0
                        maint_cost[f'i{inv_num}'] = 0
                        ft_sample[f'i{inv_num}'] = 2100

                    # parameter preset before start of simulation in window2
                    eur_proposed = values1['-drift_inv1-']
                    input_eur = {'i1': eur_population, 'i2': eur_proposed}
                    input_scale_dict = {}
                    for inv_num in inv_num_range:
                        input_scale_dict [f'i{inv_num}'] = weibull_dict [input_eur [f'i{inv_num}']]
                    input_c_p = values1['-pmc_inv1-']
                    input_c_f = values1['-cmc_inv1-']

                    '''
                    # test code
                    eur_proposed = 0.1
                    input_c_p = 1500
                    input_c_f = 6000
                    '''

                    for day in tqdm(range (0, simulation_end_days+simulation_step_days, simulation_step_days)):
                        for inv_num in inv_num_range:
                            '''
                            # test code
                            inv_num = 1
                            '''

                            plot_data[f'i{inv_num}'], [maint_day, maint_type, maint_na_days, maint_cost, ft_sample,
                                                       day_it] = inv_simulation(inv_num, input_scale_dict, input_c_p,
                                                                                input_c_f, na_days_pm, na_days_cm,
                                                                                simulation_end_days,
                                                                                simulation_step_days, day, day_it,
                                                                                maint_day, maint_type, maint_na_days,
                                                                                maint_cost, ft_sample)

                        for inv_num in inv_num_range:
                            day_it[f'i{inv_num}'] = day_it[f'i{inv_num}'] + simulation_step_days

                    break  # Exit the loop if no warning is raised

                except RuntimeWarning as e:
                    logger.info(f'Caught a RuntimeWarning: {e}, re-start the simulation. ')
                    continue  # Continue to the next iteration if warning is raised

        # Initialize looping control variables
        looping = False


        # Define the layout for the second window
        layout3 = [
            [sg.Push(), sg.Text('Prognostic Module for Solar Inverters - Output (Comparison of O&M Framework)', font=('Helvetica', 18), justification='c', expand_x=True), sg.Push()],
            [sg.Push(), sg.Text(f'SAME EUR (Inverter Equivalent Under-sizing Rate) = {eur_proposed}', font=('Helvetica', 16), justification='c', expand_x=True), sg.Push()],
            [sg.HSep()],
            # [sg.Push(), sg.Text('Inverter 1', font=("Helvetica", inv_title_size, "bold")), sg.Push()],
            [sg.Col([[sg.Text('BENCHMARK', font=("Helvetica", inv_title_size, "bold"), size = (11,1))]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv1_fig3-")]], p=0)],
            [sg.HSep()],
            # [sg.Push(), sg.Text('Inverter 2', font=("Helvetica", inv_title_size, "bold")), sg.Push()],
            [sg.Col([[sg.Text('PROPOSED', font=("Helvetica", inv_title_size, "bold"), size = (11,1))]], p=0), sg.VSep(),
             sg.Col([[sg.Canvas(key="-inv2_fig3-")]], p=0)],
            [sg.HSep()],

            # [sg.Sizer(1, 40)],
            [sg.HSep()],
            [sg.Text(
                'This tool is based upon work supported by the U.S. Department of Energy Office of Energy Efficiency and Renewable Energy (EERE) under the Solar Energy Technologies Office Award Number 39640.',
                font=('Helvetica', 10), justification='r', expand_x=True)],
        ]

        window3 = sg.Window('Prognostic Module for Solar Inverters - Output', layout3, resizable=True, finalize=True)

        # Initialize the canvas and figure
        canvas_fig_ax_dict = {}
        for inv_num in inv_num_range:
            for canvas_num in range (3,4):
                canvas_fig_ax_dict [f'canvas_i{inv_num}_f{canvas_num}'] = window3[f'-inv{inv_num}_fig{canvas_num}-'].TKCanvas
                canvas_fig_ax_dict[f'fig_i{inv_num}_f{canvas_num}'], canvas_fig_ax_dict[f'ax_i{inv_num}_f{canvas_num}'] = plt.subplots(1,2,figsize=(12,5))
                canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f{canvas_num}'] = FigureCanvasTkAgg(canvas_fig_ax_dict[f'fig_i{inv_num}_f{canvas_num}'], master=canvas_fig_ax_dict[f'canvas_i{inv_num}_f{canvas_num}'])
                canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f{canvas_num}'].draw()
                canvas_fig_ax_dict [f'plot_canvas_i{inv_num}_f{canvas_num}'].get_tk_widget().pack(side="top", fill="both", expand=True)


        while True:
            event3, values3 = window3.read(timeout=50)
            # event2, values2 = window2.read()

            # If the second window is closed, exit the program
            if event3 == sg.WINDOW_CLOSED:
                import time
                timestr = time.strftime("%Y%m%d-%H%M%S")
                for inv_num in inv_num_range:
                    canvas_fig_ax_dict[f'fig_i{inv_num}_f3'].savefig(
                        f'./figure_results_save/eur_{eur_proposed}_time_' + timestr + f'_inv_{inv_num}.png')

                window1.close()
                window3.close()
                break

            try:
                for inv_num in inv_num_range:
                    draw_plot_f3(inv_num, canvas_fig_ax_dict, day, day_it, plot_data, maint_na_days, maint_cost, eur_proposed)


            except Exception as Argument:
                logging.exception("Error in window 3 operation")

                sg.popup_error('Something is not Correct, Exiting...')


    # If the first window is closed, exit the program
    if event1 == sg.WINDOW_CLOSED:
        break

# Close all windows when the program exits
window1.close()





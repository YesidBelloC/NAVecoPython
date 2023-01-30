#Auteur : Yesid BELLO
#Date : 11/06/2022
#Programme qui permet de récupérer, à partir d'une adresse de départ et d'arrivée, les coordonnées du départ et de l'arrivée, le trajet, la vitesse et la pente de la route.
# Modifie par: Yesid BELLO

import numpy as np
import matplotlib.pyplot as plt
from casadi import *
from casadi.tools import *
import pdb
import sys
import do_mpc
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time
import random
import statistics

sys.path.append('C:/Users/crybelloceferin/Documents/MATLAB/NAVeco2022Script')

from aDataRecovery import aDataRecovery
from bVehicule_model import bVehicule_model
from bMPCParam import bMPCParam
from bSimulator import bSimulator


def main():

    ## Data recovery
    print("Running NAVeco Algorithm!")
    departure_adress = 'Expleo, Avenue des Prés, Montigny-le-Bretonneux'
    arrival_adress = 'Crédit Agricole - SQY Park, 83 Bd des Chênes, 78280 Guyancourt' #
    DevelopperMode = True
    DevelopperModeMPC = True
    Data = aDataRecovery(departure_adress,arrival_adress,DevelopperMode)

    print(len(Data))
    print(Data[-1][3]) #Distance
    print(Data[-1][4]) # Max Vitesse
    print(Data[-1][5]) # Pente
    print(Data[-1][6]) # Altitude
    print(Data[-1][7]) # Duree

    Distance = []
    Speed = []
    Pente = []

    for element in range(1,len(Data)):
        Distance.append(float(Data[element][3]))
        Speed.append(float(Data[element][4]))
        Pente.append(float(Data[element][5]))

    ## MPC Controller
    # User settings:
    show_animation = False
    store_results = False
    sample_Time = 1.0
    Objective = Data[-1][3]
    Iteration_Time = ceil(Data[-1][7]/sample_Time)
    InitialVmax = float(Data[1][4])

    # Get configured do-mpc modules:
    model = bVehicule_model()
    mpc = bMPCParam(model,InitialVmax,Objective)
    simulator = bSimulator(model)
    estimator = do_mpc.estimator.StateFeedback(model)

    # Set initial state
    time_list = []
    time_start = time.process_time()

    X_0 = 0.0
    V_0 = 0.0
    E_0 = 0.0
    x0 = np.array([X_0, V_0, E_0])

    xs = []
    vs = []
    es = []
    us = [0]

    xs.append(float(x0[0]))
    vs.append(float(x0[1]))
    es.append(float(x0[2]))

    mpc.x0 = x0
    simulator.x0 = x0
    estimator.x0 = x0

    mpc.set_initial_guess()

    # MPC Boucle
    for k in range(int(Iteration_Time)):
        tic = time.process_time()
        u0 = mpc.make_step(x0)
        toc = time.process_time()

        # Rendement variation
        if float(u0)<0:
            p_num = simulator.get_p_template()
            p_num['Eff'] = 0.2
            def p_fun(t_now):
                return p_num
            simulator.set_p_fun(p_fun)
        else:
            p_num = simulator.get_p_template()
            p_num['Eff'] = 1/0.8
            def p_fun(t_now):
                return p_num
            simulator.set_p_fun(p_fun)
        y_next = simulator.make_step(u0)
        x0 = estimator.make_step(y_next)

        # Max speed variation
        closest = min(Distance, key=lambda x: abs(x-float(x0[0])))
        index = Distance.index(closest)
        if Speed[index]!=InitialVmax:
            mpc = bMPCParam(model,Speed[index],Objective)
            mpc.x0 = x0
            mpc.set_initial_guess()
            InitialVmax = Speed[index]
        else:
            print('Exception')

        # Pente variation
        tvp_template = mpc.get_tvp_template()
        def tvp_fun(t_now):
            tvp_template['_tvp',:, 'Theta'] = Pente[index]
            return tvp_template
        mpc.set_tvp_fun(tvp_fun)


        # tvp_template = mpc.get_tvp_template()
        # if float(x0[0])>500:
        #     def tvp_fun(t_now):
        #         tvp_template['_tvp',:, 'Theta'] = 0.1
        #         return tvp_template
        #     mpc.set_tvp_fun(tvp_fun)
        # else:
        #     tvp_template = mpc.get_tvp_template()
        #     def tvp_fun(t_now):
        #         tvp_template['_tvp',:, 'Theta'] = -0.1
        #         return tvp_template
        #     mpc.set_tvp_fun(tvp_fun)

        xs.append(float(x0[0]))
        vs.append(float(x0[1]))
        es.append(float(x0[2]))
        us.append(float(u0[0]))

        time_list.append(toc-tic)

    time_arr = np.array(time_list)
    mean = np.round(np.mean(time_arr[1:])*1000)
    var = np.round(np.std(time_arr[1:])*1000)
    time_elapsed = (time.process_time() - time_start)
    if DevelopperModeMPC:
        print(' ')
        print(' ')
        print('mean runtime:{}ms +- {}ms for MPC step'.format(mean, var))
        print(time_elapsed)
        print(' ')
        print(' ')

    # Plots
    if DevelopperModeMPC:
        plt.subplot(4,1,1)
        # plt.figure(figsize=(10,4))
        plt.plot(xs)
        #plt.fill_between(DistCum,theta_vals_int,alpha=0.1)
        plt.ylabel("Distance (m)")
        plt.xlabel("Temps (s)")
        plt.grid()
        # plt.show()

        plt.subplot(4,1,2)
        # plt.figure(figsize=(10,4))
        plt.plot(vs)
        #plt.fill_between(DistCum,theta_vals_int,alpha=0.1)
        plt.ylabel("Vitesse (m/s)")
        plt.xlabel("Temps (s)")
        plt.grid()
        # plt.show()

        plt.subplot(4,1,3)
        # plt.figure(figsize=(10,4))
        plt.plot(es)
        #plt.fill_between(DistCum,theta_vals_int,alpha=0.1)
        plt.ylabel("Energie (Ws)")
        plt.xlabel("Temps (s)")
        plt.grid()
        # plt.show()

        plt.subplot(4,1,4)
        # plt.figure(figsize=(10,4))
        plt.plot(us)
        #plt.fill_between(DistCum,theta_vals_int,alpha=0.1)
        plt.ylabel("Couple (Nm)")
        plt.xlabel("Temps (s)")
        plt.grid()
        plt.show()


if __name__ == "__main__":
    main()
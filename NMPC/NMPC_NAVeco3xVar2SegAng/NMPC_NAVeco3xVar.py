import numpy as np
import matplotlib.pyplot as plt
from casadi import *
from casadi.tools import *
import pdb
import sys
sys.path.append('C:/Users/crybelloceferin/Documents/MATLAB/BoubacarDIALLO/PythonController/NMPC_NAVeco3xVar')
import do_mpc

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time

from modelNAVeco import modelNAVeco
from mpcNAVeco import mpcNAVeco
from simulatorNAVeco import simulatorNAVeco

def Eff_fun(T,Ep,En):
    if T>=0:
        Eff_val=1/Ep
    else:
        Eff_val=En

    return Eff_val

#Information:  https://www.do-mpc.com/en/latest/index.html

""" User settings: """
show_animation = False
store_results = False
sample_Time = 1.0

"""
Get configured do-mpc modules:
"""

model = modelNAVeco()
mpc = mpcNAVeco(model)
simulator = simulatorNAVeco(model)
estimator = do_mpc.estimator.StateFeedback(model)



"""
Set initial state
"""
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

"""
Run MPC main loop:
"""

for k in range(60):
    tic = time.process_time()
    u0 = mpc.make_step(x0)
    toc = time.process_time()
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
    if float(x0[0])>500:
        tvp_template = mpc.get_tvp_template()
        def tvp_fun(t_now):
            tvp_template['_tvp',:, 'Theta'] = 0.1
            return tvp_template
        mpc.set_tvp_fun(tvp_fun)
    else:
        tvp_template = mpc.get_tvp_template()
        def tvp_fun(t_now):
            tvp_template['_tvp',:, 'Theta'] = 0
            return tvp_template
        mpc.set_tvp_fun(tvp_fun)

    xs.append(float(x0[0]))
    vs.append(float(x0[1]))
    es.append(float(x0[2]))
    us.append(float(u0[0]))

    time_list.append(toc-tic)

time_arr = np.array(time_list)
mean = np.round(np.mean(time_arr[1:])*1000)
var = np.round(np.std(time_arr[1:])*1000)
print('mean runtime:{}ms +- {}ms for MPC step'.format(mean, var))

time_elapsed = (time.process_time() - time_start)
print(time_elapsed)

ec = []
EnergieCalculeTemp = 0
xc = []
PossitionCalculeTemp = 0
effm = 0.8
effr = 0.2
Rw = 0.3099

for j in range(len(us)):


    Couple = float(us[j])
    Eff = Eff_fun(Couple,effm,effr)
    # print(Eff)
    Puissance = (us[j]/Rw)*vs[j]*(Eff)

    EnergieCalculeTemp = EnergieCalculeTemp+Puissance*sample_Time
    PossitionCalculeTemp = PossitionCalculeTemp+vs[j]*sample_Time

    ec.append(float(EnergieCalculeTemp))
    xc.append(float(PossitionCalculeTemp))

plt.subplot(4,1,1)
# plt.figure(figsize=(10,4))
plt.plot(xs)
plt.plot(xc,'--')
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
plt.plot(ec,'--')
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
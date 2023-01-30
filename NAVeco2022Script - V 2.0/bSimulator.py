import numpy as np
from casadi import *
from casadi.tools import *
import pdb
import sys
sys.path.append('../../')
import do_mpc


def bSimulator(model):

    simulator = do_mpc.simulator.Simulator(model)

    _u = model.u

    params_simulator = {
        'integration_tool': 'cvodes',
        'abstol': 1e-10,
        'reltol': 1e-10,
        't_step': 1.0,
    }

    simulator.set_param(**params_simulator)

    p_num = simulator.get_p_template()
    p_num['Eff'] = 1/0.8
    def p_fun(t_now):
        return p_num
    simulator.set_p_fun(p_fun)

    tvp_template = simulator.get_tvp_template()
    def tvp_fun(t_now):
        return tvp_template
    simulator.set_tvp_fun(tvp_fun)

    simulator.setup()

    return simulator
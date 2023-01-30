import numpy as np
from casadi import *
from casadi.tools import *
import pdb
import sys
sys.path.append('../../')
import do_mpc


def bMPCParam(model,Vmax,Objective):

    mpc = do_mpc.controller.MPC(model)

    setup_mpc = {
        'n_horizon': 20,
        'n_robust': 0,
        'open_loop': 1,
        't_step': 1.0,
        'state_discretization': 'collocation',
        'collocation_type': 'radau',
        'collocation_deg': 2,
        'collocation_ni': 2,
        'store_full_solution': False,
        # Use MA27 linear solver in ipopt for faster calculations:
        # 'nlpsol_opts': {'ipopt.linear_solver': 'MA27'}
        'nlpsol_opts': {'ipopt.tol':1e-1},
        'nlpsol_opts': {'ipopt.max_iter':100},
        'nlpsol_opts': {'ipopt.mu_strategy':'adaptative'},
        'nlpsol_opts': {'ipopt.hessian_approximation':'limited-memory'},
        'nlpsol_opts': {'ipopt.limited_memory_max_history':6},
        'nlpsol_opts': {'ipopt.limited_memory_max_skipping':1},
        'nlpsol_opts': {'ipopt.print_level':0}
        # 'nlpsol_opts': {'print_time':0}
        # 'ipopt.sb': 'yes'
    }

    mpc.set_param(**setup_mpc)

    _x = model.x
    _u = model.u

    # stageCost = e1.*e1+1e-3*x3p+u1.*u1.*1e-5;

    mterm = 0*(_x['X'] - Objective)**2
    lterm = ((_x['X'] - Objective)**2)+1e-3*_x['E']+(_u['T']**2)*1e-5
    # mterm = (_x['V'] - 20)**2
    # lterm = (_x['V'] - 20)**2

    mpc.set_objective(mterm=mterm, lterm=lterm)

    mpc.set_rterm(T=0) # penalty on input changes

    mpc.bounds['lower', '_x', 'X'] = 0.0
    mpc.bounds['lower', '_x', 'V'] = 0.0
    # mpc.bounds['lower', '_x', 'E'] = 0.0

    # mpc.bounds['upper', '_x','X'] = 10000
    mpc.bounds['upper', '_x','V'] = Vmax
    # mpc.bounds['upper', '_x','E'] = 300000000000000000000

    mpc.bounds['lower','_u','T'] = -1000.0
    mpc.bounds['upper','_u','T'] =  1000.0

    Eff_var = np.array([1.25, 0.8, 0.2])
    Theta_var = np.array([0.1, 0, -0.1])
    # mpc.set_uncertainty_values(Eff = Eff_var, Theta = Theta_var)
    mpc.set_uncertainty_values(Eff = Eff_var)

    tvp_template = mpc.get_tvp_template()
    def tvp_fun(t_now):
        return tvp_template
    mpc.set_tvp_fun(tvp_fun)

    mpc.setup()

    return mpc
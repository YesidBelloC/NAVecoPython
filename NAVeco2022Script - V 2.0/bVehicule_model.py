
import numpy as np
from casadi import *
from casadi.tools import *
import pdb
import sys
sys.path.append('../../')
import do_mpc


def bVehicule_model():
    model_type = 'continuous' # either 'discrete' or 'continuous'
    model = do_mpc.model.Model(model_type)

    # Certain parameters
    #Parametros ctes Peugeot 208
    p = 0
    Cr = 0.01  #[N/rad] Coef long delantero asociado al relacion (slip rate) deslizamiento
    Rw = 0.3099 #Rayon de la roue
    M  = 1500  #[kgr] % 208 1100 308 1300 508 1500

    #Parametros ctes entorno
    g    =9.81      #[m/s2] gravedad.
    pair =1.25      #[Kg/m3] Masa volumetrica aire
    SCx  =2.2*0.11  #Coef aerodinamique 208 0.61 308 0.63 508 0.58

    #Parametros ctes rendement
    Ig      = 14.5770
    maxRPM  = Ig*30*33/(Rw*np.pi)
    maxTorq = 1000
    Krpm  = 5e-09
    Ktorq = 1e-07

    # States struct (optimization variables):
    X = model.set_variable('_x',  'X')  # distance
    V = model.set_variable('_x',  'V')  # speed
    E = model.set_variable('_x',  'E')  # Energy

    # Input struct (optimization variables):
    T = model.set_variable('_u',  'T')

    # Fixed parameters:
    Eff = model.set_variable('_p', 'Eff')
    #Theta = 0
    Theta = model.set_variable('_tvp', 'Theta')

    # algebraic equations
    Faer = 0.5*pair*SCx*V**2; #Pendiente encontrar relacion entre direction del viento y del vehiculo.
    Frr  = M*g*Cr*cos(Theta);
    Fw   = M*g*sin(Theta);

    RPMwh  = 30*V/(Rw*np.pi) # RPM de la roue
    RPM    = Ig*RPMwh          # RPM du moteur
    RPMopt = maxRPM/3          # 1/3 de RPM max
    u1opt  = (2/5)*maxTorq     # 2/5 du couple max

    # Fixed parameters:
    Reduction = ((RPM-RPMopt)**2)*Krpm+((T-u1opt)**2)*Ktorq
    # effm = 0.9 - ((RPM-RPMopt)**2)*Krpm - ((T-u1opt)**2)*Ktorq
    # effr = 0.74 - ((RPM-RPMopt)**2)*Krpm - ((T-u1opt)**2)*Ktorq


    # Differential equations
    model.set_rhs('X', V)
    model.set_rhs('V', ((T)/Rw-Faer-Frr-Fw)/M)
    model.set_rhs('E', ((T)/Rw*V*(Eff)))

    # Build the model
    model.setup()

    return model
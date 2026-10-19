import numpy as np
from . import HBV

param_names  = np.array(["Ts", "CFMAX", "CFR", "CWH", "BETA", "LP", "FC", "PERC", "K0", "K1", "K2", "UZL", "MAXBAS"])
param_bounds = np.array([[-3, 0, 0, 0, 0, 0.2, 1e-6, 0, 5e-3, 1e-3, 1e-3, 0, 1], [3, 20, 1, 0.8, 7, 5, 2000, 100, 0.99, 0.8, 0.2, 250, 10]]).T


def run_hbv(P, T, PET, params, initial_conditions=0, model=HBV):

    # preallocate memory for the states and fluxes
    states_and_fluxes = np.zeros((18, P.shape[0]))

    # write the forcings into the preallocated array
    states_and_fluxes[0] = P
    states_and_fluxes[1] = T
    states_and_fluxes[2] = PET

    # reset initial conditions
    states_and_fluxes[3:8] = initial_conditions
    states_and_fluxes[8:]  = 0.0

    # run the HBV model on the preallocated array
    model.run_hbv(states_and_fluxes, params)

    # return the runoff variable and states and fluxes
    return states_and_fluxes[-1], states_and_fluxes[3:8], states_and_fluxes[8:]

# P, T, PET,   VS, VL, SM, UZ, LZ,    RFZ, MLT, RAIM, EA, RU, RL, Q0, Q1, QQ, Q = range(18)
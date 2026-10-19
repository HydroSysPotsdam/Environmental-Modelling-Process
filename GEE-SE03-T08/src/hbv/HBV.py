"""
This is my implementation to the HBV model which is as close to the original description as possible.
Importantly, it calculates AET based on the soil moisture ot the beginning of the time step, before adding precipitation.
"""

import numpy as np

try:
    from numba import njit
except ImportError:
    print("Numba not available, no acceleration will be applied.")
    def njit(func):
        return func


@njit
def clamp(x, a_min, a_max):
    if x < a_min:
        return a_min
    elif x > a_max:
        return a_max
    else:
        return x


@njit
def run_hbv(vrs, params):

    # grab the current parameters
    ts, cfmax, cfr, cwh, beta, lp, fc, perc, k0, k1, k2, uzl, maxbas = params

    # variable indices for readability
    P, T, PET,   VS, VL, SM, UZ, LZ,    RFZ, MLT, RAIM, EA, RU, RL, Q0, Q1, QQ, Q = range(18)

    # grab the number of timesteps
    tmax = vrs.shape[1]

    for t in range(tmax):

        # use the storages from the previous step
        if t > 0:
            vrs[3:8, t] = vrs[3:8, t-1]

        ##############
        # SNOW ROUTINE
        ##############

        if vrs[T, t] < ts:

            # accumulate snowfall
            vrs[VS, t] += vrs[P, t]

            # refreeze
            vrs[RFZ, t] = cfr*cfmax*(ts - vrs[T, t])
            vrs[RFZ, t] = clamp(vrs[RFZ, t], 0, vrs[VL, t])
            vrs[VS, t] += vrs[RFZ, t]
            vrs[VL, t] -= vrs[RFZ, t]

        else:

            # snowmelt
            vrs[MLT, t] = cfmax*(vrs[T, t] - ts)
            vrs[MLT, t] = clamp(vrs[MLT, t], 0, vrs[VS, t])
            vrs[VS, t] -= vrs[MLT, t]
            vrs[VL, t] += vrs[MLT, t] + vrs[P, t]

        # release from the snowpack
        vrs[RAIM, t] = vrs[VL, t] - cwh*vrs[VS, t]
        vrs[RAIM, t] = clamp(vrs[RAIM, t], 0, vrs[VL, t])
        vrs[VL, t] -= vrs[RAIM, t]

        ##############
        # SOIL ROUTINE
        ##############

        # recharge based on rain and melt
        vrs[RU, t]  = vrs[RAIM, t] * (vrs[SM, t] / fc) ** beta
        vrs[RU, t]  = clamp(vrs[RU, t], 0, vrs[RAIM, t])

        # evapotranspiration
        vrs[EA, t]  = vrs[PET, t] * clamp(vrs[SM, t] / (fc * lp), 0, 1)
        vrs[EA, t]  = clamp(vrs[EA, t], 0, vrs[SM, t])

        # update the soil storage
        vrs[SM, t] += vrs[RAIM, t] - vrs[RU, t] - vrs[EA, t]

        # saturation excess flow
        vrs[QQ, t]  = vrs[SM, t] - fc
        vrs[QQ, t]  = clamp(vrs[QQ, t], 0, vrs[SM, t])
        vrs[SM, t] -= vrs[QQ, t]

        # clamp the soil moisture for numerical stability
        vrs[SM, t] = clamp(vrs[SM, t], 0, fc)

        ####################
        # SUBSURFACE ROUTINE
        ####################

        # add recharge to upper zone
        vrs[UZ, t] += vrs[RU, t]

        # runoff from upper zone
        vrs[Q0, t]  = k1 * vrs[UZ, t] + k0 * clamp(vrs[UZ, t] - uzl, 0, vrs[UZ, t])
        vrs[Q0, t]  = clamp(vrs[Q0, t], 0, vrs[UZ, t])
        vrs[UZ, t] -= vrs[Q0, t]

        # percolation to lower zone
        vrs[RL, t]  = min(vrs[UZ, t], perc)
        vrs[UZ, t] -= vrs[RL, t]

        # add percolation to lower zone
        vrs[LZ, t] += vrs[RL, t]

        # runoff from lower zone
        vrs[Q1, t]  = k2*vrs[LZ, t]
        vrs[Q1, t]  = clamp(vrs[Q1, t], 0, vrs[LZ, t])
        vrs[LZ, t] -= vrs[Q1, t]

    # total runoff
    vrs[Q] = vrs[Q0] + vrs[Q1] + vrs[QQ]

    #################
    # ROUTING ROUTINE
    #################

    # generate a triangular-shaped kernel
    # we use MASBAS + 2 points, because the outermost points would be zero
    # linspace creates MAXBAS + 2 points between 0 and 1, inluding the endpoints
    k = np.linspace(0, 1, int(maxbas) + 2)[1:-1]
    k = 2 * np.abs(k - np.floor(k + 0.5))
    k = k / k.sum()

    # please make sure that the convolution of an impulse at zero
    # results in a triangle with its maximum at MAXBAS//2
    vrs[Q] = np.convolve(vrs[Q], k)[:tmax]
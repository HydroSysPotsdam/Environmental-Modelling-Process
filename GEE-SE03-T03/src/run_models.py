import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import seaborn as sns

from SAFEpython.model_execution import model_execution # module to execute the model
from SAFEpython import HBV
from SAFEpython import HyMod

import process_camels as pc

# (1) Reading in the data
# !!!! 
# Be sure to change the parameters for the models as well
# if you change the data intput.
# Two lines need to be changed that set the array "param" (for HBV additonally the array "param_s")
# for each of the two models.
# !!!!
caravan_file = "camelsgb_33024" # options: camelsgb_33024, camels_11124500, hysets_10BE007
df = pc.process_input(f"{caravan_file}.csv")

# Prepare the model intput for both models
P = df["P [mm/day]"].to_numpy()
ept = df["PET [mm/day]"].to_numpy()
temp = df["T [C]"].to_numpy()

# We only want to analyze the last year but the models need a spinn-up phase to initalize the storages
# We thus run the same year 10-times
P = np.tile(P, 10)
ept = np.tile(ept, 10)
temp = np.tile(temp, 10)

# Specific model parameters

# ---------- HBV -----------
"""
Expects a numpy array with the following:
0. BETA   = Exponential parameter in soil routine [-]
1. LP     = evapotranspiration limit [-]
2. FC     = field capacity [mm]
3. PERC   = maximum flux from Upper to Lower Zone [mm/Dt]
4. K0     = near surface flow coefficient (ratio) [1/Dt]
5. K1     = upper Zone outflow coefficient (ratio) [1/Dt]
6. K2     = lower Zone outflow coefficient (ratio) [1/Dt]
7. UZL    = near surface flow threshold [mm]
8. MAXBAS = flow routing coefficient [Dt]
"""
# Snow parameters
"""
0. Ts    = threshold temperature [C]
1. CFMAX = degree day factor [mm/C]
2. CFR   = refreezing factor [-]
3. CWH   = water holding capacity of snow [-]

temp = time series of temperature
prec = time series of precipitation

    Output:
         P = time series of simulated flow exiting from the snowpack (as a result of melt-refreezing)
             [mm/Dt]
    STATES = time series of simulated storages (all in mm)
             1st column: water content of snowpack
                         (snow component)
             2nd column: water content of snowpack
                         (liquid component)
    FLUXES = time series of simulated fluxes (all in mm/Dt)
             1st column: refreezing
             2nd column: snowmelt
"""

# !!! Change the parameters here
# For camelsgb_33024.csv
param= np.array([1.2, 0.3, 50, 5.9, 0.2, 0.15, 0.01, 12, 1.3])
param_s=np.array([2.5, 5, 0.05, 0.1])

# For camels_11124500.csv
#param= np.array([1, 1, 500, 4, 0.3, 0.2, 0.01, 38, 1])
#param_s=np.array([0.8, 4.5, 0.04, 0.2])

# For hysets_10BE007.csv
#param= np.array([1, 1, 50, 0.5, 0.05, 0.01, 0.1, 72, 2])
#param_s=np.array([-2, 1, 0.05, 0])

"""
Case = flag for preferred path in the Upper Zone
            flag=1 -> Preferred path is runoff
            flag=2 -> Preferred path is percolation
"""
Case = 1
p_s, states, fluxes = HBV.snow_routine(param_s, temp, P)

# Possible to set the inital storages here
ini = np.array([0,0,0])
# Run the HBV model
q_sim, states, fluxes = HBV.hbv_sim(param, p_s, ept, Case, ini)

"""
STATES = time series of simulated storages
              0: water content of soil (soil moisture)
              1. water content of upper reservoir of flow
                 routing routine
              2. water content of lower reservoir of flow  - numpy.ndarray(T,5)
                 routing routine
FLUXES = time series of simulated fluxes
              0: actual evapotranspiration
              1: recharge (water flux from soil moisture
                 accounting module to flow routing module)
              2: percolation (water flux from upper to
                 lower reservoir of the  flow routing module)
              3: runoff from upper reservoir
              4: runoff from lower reservoir
"""


# Save only the last 365 days in a dataframe to plot the outputs
df_model = pd.DataFrame({'Q [mm/day]': q_sim[-365:], 'ET [mm/day]': fluxes.T[0][-365:], 'Date': df["Date"].to_numpy()})
df_model["Model"] = "HBV"

#-------------- HyMod -------------
"""
1. Sm   = maximum soil moisture [mm]
2. beta = exponent in the soil moisture routine [-]
3. alfa = partition coefficient [-]
4. Rs   = slow reservoir coefficient [1/Dt]
5. Rf   = fast reservoir coefficient [1/Dt]

Recommended parameter values:  Smax should fall in [0,400] (mm)
                                   beta should fall in [0,2] (-)
                                   alfa should fall in [0,1] (-)
                                     Rs should fall in [0,k] (-)
                                     Rf should fall in [k,1] (-) with 0 < k < 1
"""

# !!! Change the parameters here

# For camelsgb_33024.csv
param= np.array([140, 0.5, 0.1, 0.03, 0.9])

# For camels_11124500.csv
#param= np.array([400, 0.3, 0, 0.5, 0.8])

# For hysets_10BE007.csv
#param= np.array([390, 2, 0.08, .1, 0.5])


# Run the model
q_sim, states, fluxes = HyMod.hymod_sim(param, P, ept)
df_hymod = pd.DataFrame({'Q [mm/day]': q_sim[-365:], 'ET [mm/day]': fluxes.T[0][-365:], 'Date': df["Date"].to_numpy()})
df_hymod["Model"] = "HyMod"


# Build one dataframe with a column that identifies the output
df_model = pd.concat([df_model, df_hymod])
df_model.reset_index(inplace=True)

# Create a figure that can hold multiple plots at once
# As an alternative you might want to use: https://seaborn.pydata.org/tutorial/axis_grids.html
fig, ax = plt.subplots(3, 1, figsize=(20, 12), sharex=True)

# Plot the PET
s1 = sns.lineplot(data=df, x="Date", y="PET [mm/day]", ax=ax[0], color="green")

# Get the right hand side second y-axis
a1 = ax[0].twinx()
# Plot the precipitation as inverted bar chart
sns.barplot(data=df, x="Date", y="P [mm/day]", ax=a1, label="P", color="#5a86ad")
a1.invert_yaxis()

# Plot the simulated and observed Q
sns.lineplot(data=df_model, x="Date", y="Q [mm/day]", ax=ax[1], hue="Model")

sns.lineplot(data=df, x="Date", y="Q [mm/day]", ax=ax[1], color="black", label="Observed")

# Plot ET
sns.lineplot(data=df_model, x="Date", y="ET [mm/day]", ax=ax[2], hue="Model")

## Show only the main ticks
locator = mdate.MonthLocator()
plt.gca().xaxis.set_major_locator(locator)

# display the figure to explore it
#plt.show()

# or save it directly
fig.savefig(f"model_output_{caravan_file}.png")


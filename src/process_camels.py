import os.path
import pandas as pd

# Default data path
d_path = "../data/"


def process_input(path):
    """
    Simple function that processes camels CSV files from a given folder
    path : string of input file name
    @return : a dataframe with selected variables
    """
    # Read a specific csv from the data path
    path = d_path + path
    df = pd.read_csv(path, sep=",")
    # Make sure the date is interpreted as a datetime object -> makes temporal operations easier
    df.date = pd.to_datetime(df['date'], format='%Y-%m-%d')
    # Index frame by date
    df.set_index('date', inplace=True)
    # Select only the columns we need
    df = df[["total_precipitation_sum","potential_evaporation_sum","streamflow", "temperature_2m_mean"]]
    # Rename variables
    df.columns = ["P [mm/day]", "PET [mm/day]", "Q [mm/day]", "T [C]"]
    # Select time frame
    start_date = '2002-10-01'
    end_date = '2003-09-30'
    df = df[start_date:end_date]
    # Reformat the date for plotting
    df["Date"] = df.index.map(lambda s: s.strftime('%b-%d-%y'))
    return df


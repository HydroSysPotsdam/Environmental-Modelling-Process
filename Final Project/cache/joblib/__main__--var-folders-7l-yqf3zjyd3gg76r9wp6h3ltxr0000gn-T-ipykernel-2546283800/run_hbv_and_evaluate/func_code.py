# first line: 1
@memory.cache(ignore=["data", "ofuns", "n_cpu_cores"])
def run_hbv_and_evaluate(data, ofuns, params, n_cpu_cores=-1):
    """
    Run the HBV model on a given dataset and parameter set and evaluate the model performance using the given objective functions.

    Parameters
    ----------
    data: pd.DataFrame or list of pd.DataFrame
        DataFrame containing the columns "P", "T", "PET" and "Q_obs".
        The columns "P" and "T" are precipitation and temperature, respectively. "PET" is the potential evapotranspiration and "Q_obs" is the observed discharge.
    ofuns: function or list of functions
        Objective function to evaluate the model performance. Must have the signature of (Q_obs, Q_sim).
    params: np.array of shape (n_params,) or list of np.array
        Array containing the HBV parameters in the following order: Ts, CFMAX, CFR, CWH, BETA, LP, FC, PERC, K0, K1, K2, UZL, MAXBAS.
    n_cpu_cores: int
        Number of CPU cores for parallelization (default all).
    """

    # convert dataframes and objective functions to list if not already the case
    data    = list(data) if type(data) is not list else data
    n_data  = len(data)
    ofuns   = list(ofuns) if type(ofuns) is not list else ofuns
    n_ofuns = len(ofuns)

    # shape of the parameter array
    params   = np.atleast_2d(params)
    n_params = params.shape[0]
    shape    = (n_data, n_ofuns, n_params)

    # atomic wrapper for one HBV run
    def evaluate_single(i, j, k):
        P, T, PET, Q_obs = data[i][["P", "T", "PET", "Q_obs"]].T.to_numpy()
        Q_sim, _, _ = hbv.run_hbv(P, T, PET, params[k])
        return ofuns[j](Q_obs, Q_sim)

    # run HBV fully parallelized
    print(f"running HBV {np.prod(shape)} times, this may take a while...")
    objectives = Parallel(n_jobs=-1 if n_cpu_cores=="all" else n_cpu_cores)(delayed(evaluate_single)(i, j, k) for i, j, k in np.ndindex(shape))
    return np.array(objectives).reshape(shape).squeeze()

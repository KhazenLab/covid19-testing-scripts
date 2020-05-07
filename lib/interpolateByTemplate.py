"""
This algo is to interpolate a vector with NA by templating it from another vector.
This is an alternative to linear interpolation.
Its purpose is that the interpolated Testing data never goes below the confirmed cases for daily data.

This algo was originally developed in notebook t14 in 2 versions.
The first version is the one here. The second version was written by Halim.
I prefer this version because it is:
- vectorized
- easier to debug

The second version is ipmlemented with for loops,
which makes it difficult to debug (or run line-by-line),
eg in a jupyter notebook.
"""


import numpy as np
import pandas as pd


class InterpolationError(Exception):
    pass


def interpolate_by_translation(vec_with_na, vec_template):
    """
    Input: Two vectors
    - one vector that has a single stretch of NA (could have leading/trailing NA's as well)
    - and another vector without NAs
    
    Output: First vector but with NA gap filled with the same structure as in the non-NA vector

    Note that the v02 version below is the original that was written by Halim.
    It's more compact, doesn't implement carry-forward, implements manual forward-fill, re-calculates translateFirst and scaleLast unnecessarily,
    is more difficult to debug step-by-step in the calculation, 
    """
    #print("interpolate with")
    #print(vec_with_na)
    #print(vec_template)
    
    # raise exception if template vec is not strictly cumulative
    if (vec_template.diff()<0).any():
        raise InterpolationError("This function doesnt work except with cumulative vectors for now")
        
    # raise exception if multiple na gaps
    n_na = pd.notnull(vec_with_na).sum()
    #print(vec_with_na)
    #print(n_na)
    if n_na > 2:
        raise InterpolationError("This function was designed to deal with single-stretch gaps of na")

    if n_na == 1:
      # case of single number, either to the left of the NA's, or to the right of them
      return vec_with_na
        
    tests = vec_with_na.reset_index(drop=True)
    confirmed = vec_template.reset_index(drop=True)
    
    indexMinNonNA= np.amin(np.where((tests.notna())))
    indexNAafterFirstNb = np.where((tests.isna() & (tests.index>indexMinNonNA)))[0]
    
    # if not NA's between numbers
    if len(indexNAafterFirstNb)==0:
        return vec_with_na

    # just pick any of the indeces above to calculate some common numbers
    indexCurrent = indexNAafterFirstNb[0]
    
    #print("debugging")
    #print(indexCurrent)
    #print(tests.notna())
    #print(tests.index<indexCurrent)
    #print(np.where((tests.notna() & (tests.index<indexCurrent))))
    
    indexFirst= np.amax(np.where((tests.notna() & (tests.index<indexCurrent))))
    indexLast = np.amin(np.where((tests.notna() & (tests.index>indexCurrent))))
    tests_0 = tests[indexFirst]
    conf_0 = confirmed[indexFirst]
    tests_T = tests[indexLast]
    conf_T = confirmed[indexLast]

    # if na-vec is flat, just use constant interpolation
    if tests_0 == tests_T:
        return vec_with_na.fillna(method="ffill")
    
    # raise an exception if vec_with_na is decreasing
    if tests_0 > tests_T:
        raise InterpolationError("This function is only for increasing cumulative vec_with_na")

    # translation and scaling factors
    translateFirst=tests_0-conf_0
    conf_T_tr = conf_T+translateFirst
    scaleLast=(tests_T-conf_T_tr)/conf_T_tr

    # start translating and scaling each point: non-vectorized
    #val_all = []
    #for indexCurrent in range(indexFirst, indexLast+1):
    #    x1 = (confirmed[indexCurrent]+translateFirst)
    #    x3n = (indexCurrent - indexFirst)
    #    x3d = (indexLast    - indexFirst)
    #    x2 = (1+scaleLast*(x3n/x3d))
    #    x_fl = x1*x2
    #    x_in = np.floor(x_fl)
    #    val_all.append((x1, x3n, x3d, x2, x_fl, x_in))
    #
    # build dataframe for vector calculations
    #df_interpolated = pd.DataFrame(val_all, columns=["x1", "x3n", "x3d", "x2", "x_fl", "x_in"])


    # start translating and scaling each point: vectorized
    # FIXME: doesn't filter for indexFirst .. indexLast
    #print("Warning: # FIXME: doesn't filter for indexFirst .. indexLast")
    df_interpolated = pd.DataFrame({"C": confirmed})
    df_interpolated["x1"] = df_interpolated.C + translateFirst
    df_interpolated["x3n"] = df_interpolated.index - indexFirst
    x3d = (indexLast - indexFirst)
    df_interpolated["x2"] = (1+scaleLast*(df_interpolated["x3n"]/x3d))
    df_interpolated["x_fl"] = df_interpolated.x1*df_interpolated.x2
    df_interpolated["x_in"] = np.floor(df_interpolated.x_fl)

    # carry-forward the fractions
    # Update: just skipping this step for now
    #df_interpolated["x_fr"] = df_interpolated.x_fl - np.floor(df_interpolated.x_fl)
    #df_interpolated["fr_cumul"] = df_interpolated.x_fr.cumsum()
    #df_interpolated["fr_cumul_fl"] = np.floor(df_interpolated["fr_cumul"])
    #df_interpolated["x_daily"] = df_interpolated.x_fl.diff().fillna(0) + df_interpolated.fr_cumul_fl
    #df_interpolated["x_final"] = df_interpolated["x_in"].iloc[0] + df_interpolated.x_daily.cumsum()
    #df_interpolated["x_final"] = df_interpolated["x_final"].astype(int)
    
    # alert if this cumulative is dipping
    #if ~(vec_template.diff()<0).any() & (df_interpolated["x_final"].diff()<0).any():
    #    #print(df_interpolated)
    #    print("Template is cumulative but resultant interpolation is not cumulative")

    # return the interpolated vector
    #print("internal result")
    #print(df_interpolated)

    #ret_vec = pd.concat([vec_with_na[:indexMinNonNA], df_interpolated.x_final], axis=0, ignore_index=True)
    ret_vec = pd.concat([vec_with_na[:indexMinNonNA], df_interpolated.x_in], axis=0, ignore_index=True)
    return ret_vec



# function for multi-gap

def interpolate_by_translation_multigap(vec_with_na, vec_template, country_name):
    if vec_with_na.shape[0] != vec_template.shape[0]:
        raise Exception("Both vectors need to have equal length")

    #print("Vector to treat")    
    #print(vec_with_na)

    na_idx = np.where(pd.notnull(vec_with_na))[0]
    df_gaps = pd.DataFrame({"v1": na_idx})

    #df_gaps.v1.shift(1).shape
    #df_gaps.shape
    df_gaps["v2"] = df_gaps.v1.shift(-1)
    df_gaps = df_gaps[pd.notnull(df_gaps.v2)]
    df_gaps["v2"] = df_gaps["v2"].astype(int)

    if df_gaps.shape[0]==0:
      # no gaps
      return vec_with_na

    # if vector starts with na
    if df_gaps.v1.iloc[0]!=0:
      df_gaps = pd.concat([pd.DataFrame({"v1": [0], "v2": [df_gaps.v1.iloc[0]]}), df_gaps], axis=0)

    # if vector ends with na
    if df_gaps.v2.iloc[df_gaps.shape[0]-1]!=0:
      df_gaps = pd.concat([
                           df_gaps,
                           pd.DataFrame({"v1": [df_gaps.v2.iloc[df_gaps.shape[0]-1]], "v2": [vec_with_na.shape[0]]}), 
                        ], axis=0)

    #print("Gaps")
    #print(df_gaps)

    vec_all = []
    for i in range(df_gaps.shape[0]):
        #print("")
        #print(f"Gap #{i+1}")
        idx_start = df_gaps.v1.iloc[i]
        idx_end = df_gaps.v2.iloc[i]
        sub_na = vec_with_na[idx_start:idx_end+1]
        sub_template = vec_template[idx_start:idx_end+1]
        #print('subvec')
        #print(sub_na)
        #print(sub_template)
        df_in = pd.DataFrame({"vec_na": sub_na, "vec_template": sub_template})
        #print("df_in")
        #print(df_in)
        vec_i = interpolate_by_translation(df_in.vec_na, df_in.vec_template)
        #print("solution to subvec")
        #print(vec_i)

        # v02 doesnt need this wrapper
        #vec_i = interpolate_by_translation_v02(df_in.vec_na, df_in.vec_template)
        
        if i==0:
          vec_all.append(vec_i)
        else:
          # skip first number since already covered by earlier iteration
          vec_all.append(vec_i.iloc[1:])
        
    #print('vec all')
    #print(vec_all)
    return pd.concat(vec_all, axis=0, ignore_index=True)


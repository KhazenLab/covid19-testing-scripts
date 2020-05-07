import pandas as pd
import numpy as np


def getCountryProv(r):
  """
  Combine country and province into a single string
  """
  if r.Province_State=="" or pd.isnull(r.Province_State): return r.Country_Region
  cp = "%s – %s"%(r.Country_Region, r.Province_State)
  return cp


def add_context_to_bool_loc(df, fx_group, fx_bool, conv_len):
    """
    Add some context around a boolean column in a dataframe
    """
    #np.convolve([0,0,1,0,0],[1,1,1],mode='same')

    loc_context = df.groupby(fx_group)[fx_bool].apply(lambda x: np.convolve(x, [1]*np.min([conv_len, x.shape[0]]), mode="same").astype(bool))
    loc_context = np.concatenate(loc_context.values)
    return loc_context


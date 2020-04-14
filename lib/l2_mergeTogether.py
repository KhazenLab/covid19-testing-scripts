# -*- coding: utf-8 -*-

from os.path import join
from os.path import isfile
import pandas as pd


#Combine country and province into a single string
def getCountryProv(r):
  if r.Province_State=="" or pd.isnull(r.Province_State): return r.Country_Region
  cp = "%s – %s"%(r.Country_Region, r.Province_State)
  return cp


class L2MergeTogether:

  def __init__(self, dir_gitrepo):
    # dir_gitrepo = "/content/covid19-testing"
    self.dir_gitrepo = dir_gitrepo

  def read_confirmed_cases(self):
    # Path to local data file
    # conf_fn_filename = "covid19-global-forecasting-week-1.v20200323.raw.RData"
    # conf_fn_filename = "covid19-global-forecasting-week-2.v20200330.raw.RData"
    # conf_fn_filename = "covid19-global-forecasting-week-2.v20200331.raw.RData"
    # conf_fn_filename = "covid19-global-forecasting-week-4.v20200408.raw.RData"
    conf_fn_filename = "kaggle-confirmed.csv"
    conf_fn_full = join(self.dir_gitrepo, conf_fn_filename)
    
    # code copied from notebook t4e
    if not isfile(conf_fn_full):
      raise Exception("Missing confirmed cases file")
    
    # read csv files
    conf_train=pd.read_csv(conf_fn_full)
    
    conf_train["Date"] = pd.to_datetime(conf_train["Date"])
    
    conf_train["ConfirmedCases"] = conf_train.ConfirmedCases.astype(int)
    conf_train["Fatalities"    ] = conf_train.Fatalities.astype(int)
    
    conf_train["CountryProv"] = conf_train.apply(getCountryProv, axis=1)

    # check dupes
    if conf_train[["CountryProv","Date"]].duplicated().sum()>0:
      raise Exception("Found dupes")

    self.conf_train = conf_train


  def read_totaltests(self):
    # totaltests_fn = "multiple-aggregated_owid_wiki_worldometers_biominers-v20200406.csv"
    totaltests_fn = "multiple-aggregated_owid_wiki_worldometers_biominers-gitrepo.csv"
    totaltests_fn = join(self.dir_gitrepo, totaltests_fn)
    
    if not isfile(totaltests_fn): raise Exception("Failed to find agg file")
    
    totaltests_data = pd.read_csv(totaltests_fn)
    totaltests_data["Date"] = pd.to_datetime(totaltests_data.Date)
    
    # sort
    totaltests_data.sort_values(["Location", "Date"], inplace=True)
    
    # name corrections
    totaltests_data.loc[ totaltests_data.Location=="Aruba",    "Location" ] = "Netherlands – Aruba"
    totaltests_data.loc[ totaltests_data.Location=="Cayman Islands", "Location" ] = "United Kingdom – Cayman Islands"
    totaltests_data.loc[ totaltests_data.Location=="Mayotte", "Location" ] = "France – Mayotte"
    totaltests_data.loc[ totaltests_data.Location=="South Korea", "Location" ] = "Korea, South"
    totaltests_data.loc[ totaltests_data.Location=="Taiwan", "Location" ] = "Taiwan*"
    totaltests_data.loc[ totaltests_data.Location=="Bosnia", "Location" ] = "Bosnia and Herzegovina"
    totaltests_data.loc[ totaltests_data.Location=="Bermuda", "Location" ] = "United Kingdom – Bermuda"
    totaltests_data.loc[ totaltests_data.Location=="Brunei ", "Location" ] = "Brunei"
    totaltests_data.loc[ totaltests_data.Location=="Greenland", "Location" ] = "Denmark – Greenland"
    
    # drop dupes
    totaltests_data = totaltests_data.loc[ ~totaltests_data[["Location","Date"]].duplicated(),]
    
    # Need to drop dupes
    # dim(totaltests_data) # 1485
    # dim(unique(totaltests_data[,c("Location","Date")])) # 1431
    if totaltests_data[["Location","Date"]].duplicated().sum()>0:
      raise Exception("Found dupes")
    # totaltests_data[ duplicated(totaltests_data[,c("Location","Date")]), ]
    
    if len(totaltests_data.Location.unique())<150:
      raise Exception("Got < 150 locations in the total tests data. Something is wrong")

    self.totaltests_data = totaltests_data


  def merge_conf_total(self):
    """## Merge together total tests with confirmed cases"""
    conf_train = self.conf_train

    # Down from 171 to 143 after fixing the separator to be long-dash
    n_country_missing = len(set(conf_train.CountryProv) - set(self.totaltests_data.Location))
    if n_country_missing > 160:
      raise Exception("Found %i countries with confirmed cases and without total tests. Expected 160 or less"%n_country_missing)
    
    # list of countries for which we have confirmed cases but not total tests
    # set(conf_train.CountryProv) - set(self.totaltests_data.Location)
    
    conf_train = conf_train.merge(
                       self.totaltests_data,
                       left_on=["CountryProv","Date"],
                       right_on=["Location","Date"],
                       how='left', sort=False
                    )
    del conf_train['Location']
    
    conf_train.set_index(["CountryProv","Date"], inplace=True)
    
    self.conf_train = conf_train


  def merge_country_meta(self):
    """
    eg population, long/lat
    """
    countrymeta_fn = "t11c-country_metadata.csv"
    countrymeta_fn = "%s/%s" % (self.dir_gitrepo, countrymeta_fn)
    df_pop = pd.read_csv(countrymeta_fn)

    dim_0a = self.conf_train.shape[0]
    self.conf_train = self.conf_train.reset_index(
                        ).merge(
                           df_pop[["CountryProv", "Population", "Lat", "Long"]],
                           on="CountryProv",
                           how='left', sort=False
                        )
    dim_0b = self.conf_train.shape[0]
    assert dim_0a==dim_0b

    # This should be enabled later
    # conf_train["Lat_Long"] = conf_train["Lat"].map(str)+"_"+conf_train["Long"].map(str)

  def export_count_per_source(self):
    """## Count per source of total tests"""
    
    # entries from biominers
    # sum(is.na(conf_train$total_cumul.all)) - sum(conf_train$total_cumul.source=="biominers", na.rm=T)
    # sum(conf_train$total_cumul.source=="biominers", na.rm=T)
    
    df_counts = self.conf_train.copy()
    df_counts["total_cumul.source"] = df_counts["total_cumul.source"].apply(lambda x: "NA" if pd.isnull(x) else x)
    df_counts = df_counts["total_cumul.source"].value_counts()
    df_counts
    
    # save
    from os.path import join
    df_counts.to_csv(join(self.dir_gitrepo, "count_sources.csv"), index=True)


  def add_supplementary_stats(self):
    """
    ## supplementary stat:
    - Tests per million
    - positive/negative splits
    - percentage confirmed of total
    """
    conf_train = self.conf_train.copy()
    
    import numpy as np
    conf_train["tests_per_mil"] = conf_train.apply(lambda r: np.floor(r["total_cumul.all"]	/ r["Population"] * 1e6), axis=1)
    
    # conf_train.reset_index(inplace=True)
    
    # bring back the same order as earlier versions
    colOrder = [
      "CountryProv", "Date",
      "Country_Region", "Province_State", "Id", "ConfirmedCases",
      "Fatalities", "Lat", "Long",
      #"Lat_Long", "is_validation", # lost after moving to using the kaggle dataset directly
      "total_cumul.all", "total_cumul.source", "Population", "tests_per_mil"
    ]
    
    if len(set(conf_train.columns) - set(colOrder))>0:
      raise Exception("Extra columns")
    
    if len(set(colOrder) - set(conf_train.columns))>0:
      raise Exception("Missing columns")
    
    conf_train = conf_train[colOrder]
    
    # fix few outliers where total tests < confirmed cases and is negligible
    
    # create a bi-index since it's not working in pandas
    conf_train["UID"] = conf_train["CountryProv"]+"/"+conf_train.Date.dt.strftime("%Y-%m-%d")
    conf_train.set_index("UID", inplace=True)
    
    # overwrite (sources are worldometers.info and confirmed cases are not so far from total tests)
    conf_train.loc["Burundi/2020-04-04","total_cumul.all"] = 3
    conf_train.loc["Moldova/2020-04-04","total_cumul.all"] = 752
    conf_train.loc["Senegal/2020-04-04","total_cumul.all"] = 219
    conf_train.loc["Sierra Leone/2020-04-04","total_cumul.all"] = 4
    
    #
    conf_train.reset_index(inplace=True)
    
    del conf_train["UID"]
    
    # any outliers where total tests < confirmed cases ?
    # conf_train[  conf_train["total_cumul.all"] < conf_train["ConfirmedCases"]  ].head(n=10)
    if (conf_train["total_cumul.all"] < conf_train["ConfirmedCases"]).any():
      raise Exception("found tests<confirmed")
    
    # Fix some outliers where total tests < confirmed cases
    # Update: no need after fixing the above
    # conf_train["total_cumul.all"]	= conf_train[["total_cumul.all","ConfirmedCases"]].max(axis=1)
    
    conf_train["ratio_confirmed_total_pct"] = conf_train["ConfirmedCases"]/conf_train["total_cumul.all"]*100
    # set precision to 2 digits after the decimal
    conf_train["ratio_confirmed_total_pct"] = conf_train["ratio_confirmed_total_pct"].round(2)

    conf_train["negative_cases"] = conf_train["total_cumul.all"] - conf_train["ConfirmedCases"]
    
    # check missing Lat/Long
    if pd.isnull(conf_train.Lat ).any(): raise Exception("Found some null Lats" )
    if pd.isnull(conf_train.Long).any(): raise Exception("Found some null Longs")
    
    conf_train.set_index(["CountryProv","Date"], inplace=True)

    if not (conf_train.ratio_confirmed_total_pct.fillna(0) <= 100).all():
      raise Exception("Found some conf/total > 100")

    # doesnt work with NA
    # conf_train["total_cumul.all"] = conf_train["total_cumul.all"].astype(int)

    self.conf_train = conf_train


  def to_csv_historical(self):
    save_fn = "t11c-confirmed+totalTests-historical.csv"
    save_fn = join(self.dir_gitrepo, save_fn)
    # Use na="" since arcgis.com doesn't support values for NAs
    # write.csv(conf_train, "t11c-confirmed+totalTests-v20200406-historical.csv")
    self.conf_train.reset_index().to_csv(save_fn, na_rep="", index=False) # , quote=False


  def to_csv_latestOnly(self):
    """Extract the `latestOnly` version from the historical.
    This used to be done manually with a libreoffice pivot table.
    Now from notebook t11c3
    """
    df_hist = self.conf_train.reset_index()

    # get last date for totals
    df_last_tot = df_hist.groupby("CountryProv").apply(lambda g: g.Date[pd.notnull(g["total_cumul.all"])].tail(n=1).tolist())
    df_last_tot = df_last_tot.apply(lambda v: np.NaN if len(v)==0 else v[0])
    df_last_tot = df_last_tot.reset_index().head().rename(columns={0:"Date"})
    
    # repeat for confirmed cases to fill the blanks from totals
    df_last_conf = df_hist.groupby("CountryProv").apply(lambda g: g.Date[pd.notnull(g["ConfirmedCases"])].tail(n=1).tolist())
    df_last_conf = df_last_conf.apply(lambda v: np.NaN if len(v)==0 else v[0])
    df_last_conf = df_last_conf.reset_index().head().rename(columns={0:"Date"})
    
    # merge last from totals with last from confirmed and fillna
    df_last = df_last_tot.merge(df_last_conf, how='outer', on="CountryProv", suffixes=["_tot","_conf"])
    df_last["Date"] = df_last["Date_tot"].fillna(df_last["Date_conf"])
    del df_last["Date_tot"]
    del df_last["Date_conf"]
    
    df_last = df_last.merge(df_hist, how='left', on=["CountryProv","Date"])
    df_last = df_last[["CountryProv","Date","ConfirmedCases","Fatalities","total_cumul.all","Population","tests_per_mil", "ratio_confirmed_total_pct", "negative_cases"]]

    # save to csv
    save_fn = "t11c-confirmed+totalTests-latestOnly.csv"
    df_last.to_csv(join(self.dir_gitrepo, save_fn))

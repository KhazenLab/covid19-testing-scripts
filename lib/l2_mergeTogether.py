# -*- coding: utf-8 -*-

from os.path import join
from os.path import isfile
import pandas as pd
import numpy as np
import datetime as dt


#Combine country and province into a single string
def getCountryProv(r):
  if r.Province_State=="" or pd.isnull(r.Province_State): return r.Country_Region
  cp = "%s – %s"%(r.Country_Region, r.Province_State)
  return cp


class L2MergeTogether:

  def __init__(self, dir_gitrepo):
    # dir_gitrepo = "/content/covid19-testing"
    self.dir_l0_notion = join(dir_gitrepo, "l0-notion_tables")
    self.dir_l1a_others = join(dir_gitrepo, "l1a-non-biominer_data")
    self.dir_l1b_altogether = join(dir_gitrepo, "l1b-altogether")
    self.dir_l2_withConf = join(dir_gitrepo, "l2-withConfirmed")


  def read_confirmed_cases(self):
    """
    Update 2020-04-15: this used to get kaggle data, but now it gets JHU data
    """
    # Path to local data file
    # conf_fn_filename = "covid19-global-forecasting-week-1.v20200323.raw.RData"
    # conf_fn_filename = "covid19-global-forecasting-week-2.v20200330.raw.RData"
    # conf_fn_filename = "covid19-global-forecasting-week-2.v20200331.raw.RData"
    # conf_fn_filename = "covid19-global-forecasting-week-4.v20200408.raw.RData"
    # conf_fn_filename = "kaggle-confirmed.csv"
    conf_fn_filename = "jhu-confirmed+deaths.csv"
    conf_fn_full = join(self.dir_l1a_others, conf_fn_filename)

    # code copied from notebook t4e
    if not isfile(conf_fn_full):
      raise Exception("Missing confirmed cases file")

    # read csv files
    conf_train=pd.read_csv(conf_fn_full)

    # continue
    conf_train["Date"] = pd.to_datetime(conf_train["Date"])
    conf_train["ConfirmedCases"] = conf_train.ConfirmedCases.astype(int)
    conf_train["Fatalities"    ] = conf_train.Fatalities.astype(int)
    conf_train["CountryProv"] = conf_train.apply(getCountryProv, axis=1)

    # move rename Taiwan from read_totaltests below to here
    conf_train.loc[conf_train["CountryProv"]=="Taiwan*", "CountryProv"] = "Taiwan" # drop asterisk

    # check dupes
    if conf_train[["CountryProv","Date"]].duplicated().sum()>0:
      raise Exception("Found dupes")

    # fix few outliers
    # Two steps
    # 1. create a bi-index since it's not working in pandas
    # 2. assert that the data is of a certain value (as of the check of this date 2020-04-14)
    # 2. overwrite (sources are worldometers.info and confirmed cases are not so far from total tests)
    #conf_train["UID"] = conf_train["CountryProv"]+"/"+conf_train.Date.dt.strftime("%Y-%m-%d")
    #conf_train.set_index("UID", inplace=True)
    #
    # US/Florida on 04-13: jump by 100k
    # Cannot use NaN because that converts the field to double and replaces the full csv
    # Update 2020-04-15: this outlier was fixed in kaggle
    #assert conf_train.loc["US – Florida/2020-04-12","ConfirmedCases"] == 19895
    #assert conf_train.loc["US – Florida/2020-04-13","ConfirmedCases"] == 21019 # 123019
    #conf_train.loc["US – Florida/2020-04-13","ConfirmedCases"] = 23019 # np.NaN
    #
    #conf_train.reset_index(inplace=True)
    #del conf_train["UID"]

    # dropping entries for which we have no lat/long
    drop_pairs = [
      'Canada – Diamond Princess', 'Canada – Grand Princess',
      'Canada – Recovered',
      'US',
      #'Yemen',
      #'US – American Samoa',
      'US – Diamond Princess', 'US – Grand Princess',
      #'US – Northern Mariana Islands'
    ]
    d1=conf_train.shape[0]
    conf_train = conf_train[~(conf_train.CountryProv.isin(drop_pairs))]
    d2=conf_train.shape[0]
    assert ((d2 < d1) & (d2 > 26600))

    self.conf_train = conf_train


  def read_totaltests(self):
    # totaltests_fn = "multiple-aggregated_owid_wiki_worldometers_biominers-v20200406.csv"
    totaltests_fn = "multiple-aggregated_owid_wiki_worldometers_biominers-gitrepo.csv"
    totaltests_fn = join(self.dir_l1b_altogether, totaltests_fn)

    if not isfile(totaltests_fn): raise Exception("Failed to find agg file")

    totaltests_data = pd.read_csv(totaltests_fn)
    totaltests_data["Date"] = pd.to_datetime(totaltests_data.Date)

    # sort
    totaltests_data.sort_values(["Location", "Date"], inplace=True)

    # name corrections
    def my_name_corr(n1, n2):
      if not (totaltests_data.Location==n1).any():
        print(f"Error: Useless rename from {n1} since none exists")
        return

      if (totaltests_data.Location==n2).any():
        print(f"Error: Unsafe to replace name {n1} -> {n2} since {n2} already exists")
        print(totaltests_data.set_index(["Location"]).loc[n1])
        print(totaltests_data.set_index(["Location"]).loc[n2])
        import sys
        sys.exit(1)
      totaltests_data.loc[ totaltests_data.Location==n1,    "Location" ] = n2

    # Update 2020-05-06: Renames in general should no longer be done here.
    # Taiwan specifically was moved up to the conf function above
    #my_name_corr("Aruba", "Netherlands – Aruba")
    #my_name_corr("Cayman Islands", "United Kingdom – Cayman Islands")
    #my_name_corr("Mayotte", "France – Mayotte")

    # update 2020-04-20, sticking to the "South Korea" nomenclature
    # totaltests_data.loc[ totaltests_data.Location=="South Korea", "Location" ] = "Korea, South"

    #my_name_corr("Taiwan", "Taiwan*")
    #my_name_corr("Bosnia", "Bosnia and Herzegovina")
    #my_name_corr("Bermuda", "United Kingdom – Bermuda")
    #my_name_corr("Brunei ", "Brunei")
    #my_name_corr("Greenland", "Denmark – Greenland")

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
    # only needed if how='outer' above
    # conf_train["CountryProv"] = conf_train["CountryProv"].fillna(conf_train['Location'])
    del conf_train['Location']

    # fix few outliers where total tests < confirmed cases and is negligible
    # Two steps
    # 1. create a bi-index since it's not working in pandas
    # 2. assert that the data is of a certain value (as of the check of this date 2020-04-14)
    # 2. overwrite (sources are worldometers.info and confirmed cases are not so far from total tests)
    conf_train["UID"] = conf_train["CountryProv"]+"/"+conf_train.Date.dt.strftime("%Y-%m-%d")
    conf_train.set_index("UID", inplace=True)

    assert conf_train.loc["Burundi/2020-04-04","total_cumul.all"] == 2
    conf_train.loc["Burundi/2020-04-04","total_cumul.all"] = 3 # was 2 from worldometers
    assert conf_train.loc["Moldova/2020-04-04","total_cumul.all"] == 681
    conf_train.loc["Moldova/2020-04-04","total_cumul.all"] = 752 # was 681 from worldometers
    #assert ...
    #conf_train.loc["Senegal/2020-04-04","total_cumul.all"] = 219 # no longer needed after owid/roser data source integration
    assert conf_train.loc["Sierra Leone/2020-04-04","total_cumul.all"] == 2
    conf_train.loc["Sierra Leone/2020-04-04","total_cumul.all"] = 4 # was 2 from worldometers

    # inconsistency between covidtracking.com and kaggle confirmed cases
    # As of 2020-05-06, this point is dropped
    print("US/NY/03-12:")
    print(conf_train.loc["US – New York/2020-03-12","total_cumul.all"])
    #assert conf_train.loc["US – New York/2020-03-12","total_cumul.all"] == 308
    #conf_train.loc["US – New York/2020-03-12","total_cumul.all"] = 328
    assert pd.isnull(conf_train.loc["US – New York/2020-03-12","total_cumul.all"])

    conf_train.reset_index(inplace=True)
    del conf_train["UID"]

    # continue with index as usual
    conf_train.set_index(["CountryProv","Date"], inplace=True)
    conf_train.sort_index(inplace=True)

    # check that total tests >= Confirmed cases
    conf_breach = conf_train[(conf_train["total_cumul.all"] < conf_train["ConfirmedCases"])]
    if conf_breach.shape[0] > 0:
      print("Details of exception")
      print(conf_breach.head())
      raise Exception("Found breach totals<confirmed for: (only top 5 shown above)")

    self.conf_train = conf_train


  def drop_outlaws(self):
    """
    Parallel of l1 drop_outlaws
    but for tests < confirmed
    """
    fn_wrong = join(self.dir_l2_withConf, "dropped_outlaws_l2.csv")

    df_merged = self.conf_train.reset_index().copy()
    df_merged.rename(columns={"CountryProv": "Location"}, inplace=True) # for compatibility with L1.drop_outlaws

    # identify country/state/date triplets where the number of tests < number of confirmed cases
    df_merged = df_merged[pd.notnull(df_merged["total_cumul.all"])]
    df_merged["daily_conf"] = df_merged.groupby("Location")["ConfirmedCases"].diff()
    df_merged["daily_test"] = df_merged.groupby("Location")["total_cumul.all"].diff()
    #df_merged = df_merged[(df_merged.daily_test < 0) | (df_merged.daily_test < df_merged.daily_conf)]

    loc_wrong = df_merged.daily_test < df_merged.daily_conf
    if not loc_wrong.any():
      # just clean the csv from the context entries
      #df_old = pd.read_csv(fn_wrong)
      #df_old["Date"] = pd.to_datetime(df_old.Date)
      #df_old = df_old.sort_values(["Location", "Date", "total_cumul.source"])
      #df_old = df_old.loc[pd.notnull(df_old.is_approved)]
      #df_old.to_csv(fn_wrong, index=False)
      return

    df_merged["is_wrong"] = False
    df_merged.loc[loc_wrong, "is_wrong"] = True

    #np.convolve([0,0,1,0,0],[1,1,1],mode='same')
    #loc_context = np.convolve(loc_wrong, [1]*6)
    conv_len = 6
    loc_context = df_merged.groupby("Location")["is_wrong"].apply(lambda x: np.convolve(x, [1]*np.min([conv_len, x.shape[0]]), mode="same").astype(bool))
    loc_context = np.concatenate(loc_context.values)

    df_merged["is_approved"] = False
    idx_approved = ( loc_wrong &
                     ( (df_merged["total_cumul.source"]=="worldometers")|
                       (df_merged.daily_test==0)
                     )
                   )
    df_merged.loc[idx_approved, "is_approved"] = True

    no_work_required = df_merged.loc[loc_wrong].is_approved.all()

    df_merged = df_merged[["Location", "Date", "total_cumul.source",
                           "ConfirmedCases", "total_cumul.all",
                           "daily_conf", "daily_test", "is_wrong", "is_approved"]]

    print("Found %i triplets with number of confirmed cases > number of tests. Here are the top 20:"%loc_wrong.sum())
    print(df_merged.loc[loc_wrong].head(20))

    # save wrong values into separate csv
    df_merged["is_wrong"] = df_merged.is_wrong.map(lambda x: "x" if x else "")
    df_merged["is_approved"] = df_merged.is_approved.map(lambda x: "x" if x else "")

    df_context = df_merged.loc[loc_context]

    df_old = pd.read_csv(fn_wrong)
    df_old["Date"] = pd.to_datetime(df_old.Date)

    df_new = df_context.merge(df_old, how="outer", on=["Location","Date","total_cumul.source"], suffixes=["","_old"])
    for fx in ["ConfirmedCases", "total_cumul.all", "daily_conf", "daily_test", "is_wrong", "is_approved"]:
      df_new[fx] = df_new[fx].fillna(df_new[fx+"_old"])
      del df_new[fx+"_old"]

    df_new = df_new.sort_values(["Location", "Date", "total_cumul.source"])
    df_new = df_new.loc[~df_new.duplicated()]
    df_new.to_csv(fn_wrong, index=False)

    # Note: need to re-run rather than just overwrite these values with nan so that the next-best source can provide the number
    #       Also, some cases are not easy to automate and require human judgement
    import click
    if no_work_required:
      msg = """
      WARNING: Found daily cases > daily tests => appended rows to drop in l2-withConfirmed/dropped_outlaws_l2.csv
               but all were marked as approved automatically because it is all from worldometers data.
               Just re-run l1 then l2.
      """
      click.secho(msg, fg="yellow")
    else:
      msg = """
      WARNING: Found daily cases > daily tests => appended rows to drop in l2-withConfirmed/dropped_outlaws_l2.csv
               Please mark approved (or fix) there
               then re-run l1 and l2 to re-calculate selected source per country/state/date triplet
               Hint: by default, we mark worldometers drops as approved
      """
      click.secho(msg, fg="red")

    import sys
    sys.exit(1)


  def merge_country_meta(self):
    """
    eg population, long/lat
    """
    countrymeta_fn = "t11c-country_metadata.csv"
    countrymeta_fn = "%s/%s" % (self.dir_l0_notion, countrymeta_fn)
    df_pop = pd.read_csv(countrymeta_fn)

    # rounding the Long/Lat to 6 digits
    df_pop["Long"] = df_pop.Long.round(6)
    df_pop["Lat"] = df_pop.Lat.round(6)

    # merge
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

    # make dataframe
    df_counts = pd.DataFrame(df_counts).transpose()
    df_counts["date"]=dt.datetime.now()
    df_counts = df_counts.reset_index(drop=True).set_index("date")
    df_counts["Comment"] = ""
    colorder = [
        'Comment',
        'owid/roser',
        'owid/ortiz',
        'covidtracking.com',
        'wiki',
        'worldometers',
        'biominers',
        'NA'
    ]
    colorder = colorder + sorted(list(set(df_counts.columns)-set(colorder)))
    df_counts = df_counts[colorder]

    # read current file and concatenate current counts
    fn_csv = join(self.dir_l2_withConf, "count_sources.csv")
    df_current = pd.read_csv(fn_csv)
    df_current["date"] = pd.to_datetime(df_current["date"])
    df_current.set_index("date", inplace=True)
    df_current = df_current[colorder]
    df_current = pd.concat([df_counts, df_current], axis=0)
    df_current.sort_index(ascending=True, inplace=True)

    # filter duplicates
    dcd = df_current[list(set(df_current.columns)-set(["Comment"]))].diff()
    dcd = pd.isnull(dcd).all(axis=1) | (dcd!=0).any(axis=1)
    df_current = df_current.loc[dcd,]

    # save
    #df_counts.to_csv(fn_csv, index=True)
    df_current.sort_index(ascending=False, inplace=True)
    df_current.to_csv(fn_csv, index=True)


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
      "Country_Region", "Province_State",
      #"Id",# dropped after move from kaggle to JHU
      "ConfirmedCases",
      "Fatalities",
      "Lat", "Long",
      #"Lat_Long", "is_validation", # lost after moving to using the kaggle dataset directly
      "total_cumul.all", "total_cumul.source", "Population", "tests_per_mil"
    ]

    if len(set(conf_train.columns) - set(colOrder))>0:
      raise Exception("Extra columns")

    if len(set(colOrder) - set(conf_train.columns))>0:
      raise Exception("Missing columns")

    conf_train = conf_train[colOrder]


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
    if pd.isnull(conf_train.Lat ).any():
      print("Details for exception below of null lats")
      print(conf_train[pd.isnull(conf_train.Lat )].CountryProv.unique()[:100])
      raise Exception("Found some null Lats" )

    if pd.isnull(conf_train.Long).any():
      raise Exception("Found some null Longs")

    conf_train.set_index(["CountryProv","Date"], inplace=True)

    if not (conf_train.ratio_confirmed_total_pct.fillna(0) <= 100).all():
      raise Exception("Found some conf/total > 100")

    # doesnt work with NA
    # conf_train["total_cumul.all"] = conf_train["total_cumul.all"].astype(int)

    # finally convert back to int after all
    conf_train["ConfirmedCases"] = conf_train.ConfirmedCases.astype(int)

    self.conf_train = conf_train


  def to_csv_historical(self):
    save_fn = "t11c-confirmed+totalTests-historical.csv"
    save_fn = join(self.dir_l2_withConf, save_fn)
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
    df_last_tot = df_last_tot.reset_index().rename(columns={0:"Date"})

    # repeat for confirmed cases to fill the blanks from totals
    df_last_conf = df_hist.groupby("CountryProv").apply(lambda g: g.Date[pd.notnull(g["ConfirmedCases"])].tail(n=1).tolist())
    df_last_conf = df_last_conf.apply(lambda v: np.NaN if len(v)==0 else v[0])
    df_last_conf = df_last_conf.reset_index().rename(columns={0:"Date"})

    # add a field for Date_first_totals
    df_first_tot = df_hist.groupby("CountryProv").apply(lambda g: g.Date[pd.notnull(g["total_cumul.all"])].head(n=1).tolist())
    df_first_tot = df_first_tot.apply(lambda v: np.NaN if len(v)==0 else v[0])
    df_first_tot = df_first_tot.reset_index().rename(columns={0:"Date"})

    # count number of points with totals
    df_count_tot = df_hist.groupby("CountryProv").apply(lambda g: pd.notnull(g["total_cumul.all"]).sum())
    df_count_tot = df_count_tot.reset_index().rename(columns={0:"Count"})

    # merge last from totals with last from confirmed and fillna
    df_last = df_last_tot.copy()
    df_last = df_last.merge(df_last_conf, how='outer', on="CountryProv", suffixes=["_latest_totals","_latest_confirmed"])
    df_last["Date"] = df_last["Date_latest_totals"].fillna(df_last["Date_latest_confirmed"])

    # merge first date of totals and count
    df_last = df_last.merge(df_first_tot.rename(columns={"Date": "Date_first_totals"}), how='outer', on="CountryProv")
    df_last = df_last.merge(df_count_tot.rename(columns={"Count": "Date_count_totals"}), how='outer', on="CountryProv")

    # get fields for totals based on date latest totals
    fx_totals = ["CountryProv","Date","total_cumul.all","tests_per_mil", "ratio_confirmed_total_pct", "negative_cases"]
    df_last = df_last.merge(df_hist[fx_totals], how='left', left_on=["CountryProv","Date_latest_totals"], right_on=["CountryProv","Date"])

    # get fields for confirmed based on date latest confirmed
    fx_confirmed = ["CountryProv","Date","ConfirmedCases",
                    "Fatalities",
                    "Population"]
    df_last = df_last.merge(df_hist[fx_confirmed], how='left', left_on=["CountryProv","Date_latest_confirmed"], right_on=["CountryProv","Date"])

    del df_last["Date"]
    del df_last["Date_x"]
    del df_last["Date_y"]

    # re-order columns
    df_last = df_last[[ "CountryProv", "Date_first_totals", "Date_latest_totals", "Date_count_totals", "Date_latest_confirmed", "ConfirmedCases",
                        "Fatalities",
                        "total_cumul.all", "Population", "tests_per_mil", "ratio_confirmed_total_pct", "negative_cases"]]

    # save to csv
    save_fn = "t11c-confirmed+totalTests-latestOnly.csv"
    df_last.to_csv(join(self.dir_l2_withConf, save_fn), index=False)

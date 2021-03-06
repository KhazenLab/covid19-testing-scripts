# -*- coding: utf-8 -*-

from os.path import join
import pandas as pd
import numpy as np
import tempfile
import urllib.request
import json
from .utils import add_context_to_bool_loc

import requests
import requests_cache
from datetime import timedelta
expire_after = timedelta(hours=1)
requests_cache.install_cache('demo_cache', expire_after=expire_after)
requests_cache.remove_expired_responses()


def my_download(csv_url, csv_fn, description):
    """
    To replace     urllib.request.urlretrieve(url_global, fn_global)
    and add cache
    """
    # download file
    print(f"Download: {description} to {csv_fn}: start")
    requests_cache.install_cache('demo_cache')
    r = requests.get(csv_url, stream=True)
    with open(csv_fn, 'wb') as handle:
        for block in r.iter_content(1024):
          handle.write(block)

    print(f"Download: {description}: end")



class JhuImporter:

  def __init__(self, dir_gdrive):
    self.dir_l0_notion = join(dir_gdrive, "l0-notion_tables")
    self.dir_l1a_others = join(dir_gdrive, "l1a-non-biominer_data")
    self.dir_l1b_altogether = join(dir_gdrive, "l1b-altogether")
    self.dir_temp = tempfile.mkdtemp()
 
  def get_jhu_confirmed_global(self):
    """
    Get confirmed cases from JHU github repo.
    This used to be from kaggle dataset, but it's more up-to-date to get it from JHU
    Notebook t11b4, shadi
    """
    # Download JHU csv file
    fn_global = join(self.dir_temp, "jhu-global-original.csv")
    url_global = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    my_download(url_global, fn_global, "jhu confirmed global")
    
    ## Read global"""
    df_global = pd.read_csv(fn_global)
    df_global.rename(columns={"Country/Region": "Country_Region", "Province/State": "Province_State"}, inplace=True)
    
    # convert to long format
    idx_dates=4
    assert df_global.columns[idx_dates]=="1/22/20"
    df_global = pd.melt(df_global,
            # id_vars=['Country_Region', 'Province_State', "Lat", "Long"],
            id_vars=['Country_Region', 'Province_State'],
            value_vars=df_global.columns[idx_dates:])
    
    # postprocess
    df_global.rename(columns={"variable": "Date", "value": "ConfirmedCases"}, inplace=True)
    df_global["Date"] = pd.to_datetime(df_global["Date"], format="%m/%d/%y")
    df_global = df_global.sort_values(["Country_Region", "Province_State", "Date"])
    
    # sort columns
    df_global = df_global[["Country_Region", "Province_State", "Date", "ConfirmedCases"]]

    return df_global


  def get_jhu_deaths_global(self):
    """
    Notebook t11b5 by Halim
    """
    fn_globalDeath = "time_series_covid19_deaths_global.csv"
    url_globalDeath = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    my_download(url_globalDeath, fn_globalDeath, "jhu death global")
    
    df_globalDeath = pd.read_csv(fn_globalDeath)
    df_globalDeath.rename(columns={"Country/Region": "Country_Region", "Province/State": "Province_State"}, inplace=True)

    # index of 1st date
    idx_dates=4
    assert df_globalDeath.columns[idx_dates]=="1/22/20"
    df_globalDeath = pd.melt(df_globalDeath,
            id_vars=['Country_Region', 'Province_State'],
            value_vars=df_globalDeath.columns[idx_dates:])

    df_globalDeath.rename(columns={"variable": "Date", "value": "Fatalities"}, inplace=True)
    df_globalDeath["Date"] = pd.to_datetime(df_globalDeath["Date"], format="%m/%d/%y")
    df_globalDeath = df_globalDeath.sort_values(["Country_Region", "Province_State", "Date"])

    df_globalDeath = df_globalDeath[["Country_Region", "Province_State", "Date", "Fatalities"]]

    return df_globalDeath


  def get_jhu_confirmed_usa(self):
    """
    Notebook t11b4, shadi
    """
    ## Download US file"""
    fn_usa = join(self.dir_temp, "jhu-usa-original.csv")
    url_usa = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    my_download(url_usa, fn_usa, "jhu confirmed usa")
    
    ## Read US"""
    df_usa = pd.read_csv(fn_usa)
    
    # convert to long format
    idx_dates = 11 # This is the first index of dates column
    assert df_usa.columns[idx_dates]=="1/22/20"
    df_usa = pd.melt(df_usa,
            # id_vars=['Country_Region', 'Province_State', "Admin2", "Lat", "Long_"],
            id_vars=['Country_Region', 'Province_State', "Admin2"],
            value_vars=df_usa.columns[idx_dates:])
    
    # postprocess
    df_usa.rename(columns={"variable": "Date", "value": "ConfirmedCases"}, inplace=True)
    df_usa["Date"] = pd.to_datetime(df_usa["Date"], format="%m/%d/%y")
    df_usa = df_usa.sort_values(["Country_Region", "Province_State", "Admin2", "Date"])
    
    # add up counties
    df_usa = df_usa.groupby(["Country_Region", "Province_State", "Date"]).ConfirmedCases.agg(sum)
    df_usa = df_usa.reset_index()
    
    # sort columns
    df_usa = df_usa[["Country_Region", "Province_State", "Date", "ConfirmedCases"]]

    return df_usa


  def get_jhu_deaths_usa(self):
    """
    Notebook t11b5 by Halim
    """
    
    fn_USDeath = "time_series_covid19_deaths_US.csv"
    url_USDeath = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
    my_download(url_USDeath, fn_USDeath, "jhu death usa")   

    df_USDeath = pd.read_csv(fn_USDeath)

    idx_dates = 12 # This is the first index of dates column
    assert df_USDeath.columns[idx_dates]=="1/22/20"
    df_USDeath = pd.melt(df_USDeath,
            id_vars=['Country_Region', 'Province_State', 'Admin2'],
            value_vars=df_USDeath.columns[idx_dates:])

    df_USDeath.rename(columns={"variable": "Date", "value": "Fatalities"}, inplace=True)
    df_USDeath["Date"] = pd.to_datetime(df_USDeath["Date"], format="%m/%d/%y")
    df_USDeath = df_USDeath.sort_values(["Country_Region", "Province_State", "Admin2", "Date"])

    df_USDeathcomb= df_USDeath.groupby(['Country_Region','Province_State','Date'])['Fatalities'].sum()
    df_USDeathcomb = df_USDeathcomb.reset_index()

    # sort columns
    df_USDeathcomb = df_USDeathcomb[["Country_Region", "Province_State", "Date", "Fatalities"]]

    return df_USDeathcomb



class L1ImportOthers:

  def __init__(self, dir_gdrive, do_download):
    self.dir_l0_notion = join(dir_gdrive, "l0-notion_tables")
    self.dir_l1a_others = join(dir_gdrive, "l1a-non-biominer_data")
    self.dir_l1b_altogether = join(dir_gdrive, "l1b-altogether")
    self.dir_l2_withConf = join(dir_gdrive, "l2-withConfirmed")
    self.dir_temp = tempfile.mkdtemp()
    self.jhu = JhuImporter(dir_gdrive)
    self.do_download = do_download


  def get_jhu_conf_deaths(self):
    if not self.do_download: return

    print("JHU .. downloading")
    df_conf_gl = self.jhu.get_jhu_confirmed_global()
    df_conf_us = self.jhu.get_jhu_confirmed_usa()
    df_dead_gl = self.jhu.get_jhu_deaths_global()
    df_dead_us = self.jhu.get_jhu_deaths_usa()
    print("JHU .. done")

    df_conf_both = pd.concat([df_conf_gl, df_conf_us], axis=0)
    df_dead_both = pd.concat([df_dead_gl, df_dead_us], axis=0)

    df_all = df_conf_both.merge(
               df_dead_both,
               how='inner',
               on=['Country_Region','Province_State','Date']
             )

    # sort columns
    df_all = df_all[["Country_Region", "Province_State", "Date", "ConfirmedCases", "Fatalities"]]
    df_all["ConfirmedCases"] = df_all["ConfirmedCases"].astype(int)
    df_all["Fatalities"] = df_all["Fatalities"].astype(int)

    # some renames. Usually we're renaming other sources to match with JHU, 
    # but for south korea in particular, we don't like "Korea, South", so we're renaming here
    df_all.loc[df_all.Country_Region=="Korea, South", "Country_Region"] = "South Korea"
    
    #2020-04-27 fixes for Canada Nova Scotia
    # make a new single-index since pandas multi-index seems to be broken as of version 1.0
    df_all["UID"] = df_all["Country_Region"] + " – "+ df_all["Province_State"].fillna("")+ "/" + df_all.Date.dt.strftime("%Y-%m-%d")
    if df_all["UID"].duplicated().any(): raise Exception("UID not unique")
    df_all.set_index("UID", inplace=True)
    # replacements here
    df_all.loc["Canada – Nova Scotia/2020-04-24","ConfirmedCases"] = 850
    df_all.loc["Canada – Nova Scotia/2020-04-25","ConfirmedCases"] = 865
    df_all.loc["Canada – Nova Scotia/2020-04-26","ConfirmedCases"] = 873
    
    df_all.loc["Canada – Nova Scotia/2020-04-24","Fatalities"] = 16
    df_all.loc["Canada – Nova Scotia/2020-04-25","Fatalities"] = 22
    df_all.loc["Canada – Nova Scotia/2020-04-26","Fatalities"] = 24
    # done with index, so drop it
    df_all.reset_index(inplace=True)
    del df_all["UID"]
    
    
    # sort
    df_all = df_all.sort_values(["Country_Region", "Province_State", "Date"], ascending=True)

    ## Save modified files"""
    fn_save = join(self.dir_l1a_others, "jhu-confirmed+deaths.csv")
    df_all.to_csv(fn_save, index=False)


  def _get_owid_roser_freeze_20200420(self):
    """
    Not sure if it's a good idea to do this.
    Uruguay for example lost 2 weeks in owid, and we're not sure if it's a mistake or not.
    OTOH, colombia had wrong entries altogether, and the live version fixed it.
    Also, Greece 04-16 was wrong, but re-importing the frozen dataset brings it back.
    Will keep this code and just comment out its usage from below
    """
    # This doesnt download and doesnt save to csv again since it's a frozen version
    fn_owid_roser = "ourworldindata.org-roser-freeze_20200420.csv"
    df_owid_roser = pd.read_csv(join(self.dir_l1a_others, fn_owid_roser))
    df_owid_roser["Date"] = pd.to_datetime(df_owid_roser.Date)

    # drop some countries
    df_owid_roser.set_index("Entity2", inplace=True)
    df_owid_roser.drop("Colombia", inplace=True) # weird numbers in frozen version
    df_owid_roser.reset_index(inplace=True)

    # drop some pairs
    df_owid_roser.set_index(["Entity2","Date"], inplace=True)
    df_owid_roser.drop(["Greece","2020-04-16"], inplace=True)
    df_owid_roser.reset_index(inplace=True)

    return df_owid_roser


  def get_owid_roser(self):
    """
    Download the data from ourworldindata.org that is referenced at
    https://ourworldindata.org/coronavirus#the-total-number-of-tests-performed-or-people-tested-so-far

    Update 2020-04-14:
    Replace their csv from the ourworldindata.org article (download from plot) with the one from the github repo. It contains more dates/countries

    Update 2020-04-20:
    They're sometimes dropping historical points for no apparent reason, eg Urugual 2020-03-11 till 2020-03-28 and Portugal 2020-03
    We copied these points over to our notion table to keep them.
    We're also setting a secondary ourworldindata.org/roser source which is frozen as of 2020-04-20
    This would help us avoid losing more data if they drop them
    """

    #fn_owid_roser = "multiple-ourworldindata.org page 2 roser - v20200406.csv"
    # fn_owid_roser = "multiple-ourworldindata.org page 2 roser - gitub.csv"
    fn_owid_roser = "ourworldindata.org-roser-live.csv"

    # download file
    if not self.do_download:
      self.df_owid_roser_live = pd.read_csv(join(self.dir_l1a_others, fn_owid_roser))
      self.df_owid_roser_live["Date"] = pd.to_datetime(self.df_owid_roser_live.Date)
      return

    # download
    csv_url = "https://github.com/owid/covid-19-data/raw/master/public/data/testing/covid-testing-all-observations.csv"
    my_download(csv_url, join(self.dir_temp, fn_owid_roser), "owid live")

    # Read
    df_owid_roser = pd.read_csv(join(self.dir_temp, fn_owid_roser))
    df_owid_roser.Date = pd.to_datetime(df_owid_roser.Date)
    #df_owid_roser["Cumulative total"] = df_owid_roser["Cumulative total"].astype(int)

    # drop some dupes data, with: India - samples tested, United States - specimens tested (CDC), japan - tests performed, etc
    # Ghana - people tested, Ghana - samples tested, Thailand - people tested, Thailand - samples tested
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "India - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "United States - inconsistent units (COVID Tracking Project)"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "United States - units unclear"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "Japan - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "Singapore - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "Italy - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "United Kingdom - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "Ghana - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "Thailand - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity != "Poland - people tested"]
    
    # Split the name and comment for simplicity
    ent_uniq = df_owid_roser.Entity.unique()
    df_splitname = pd.DataFrame([x.split("-") for x in ent_uniq], columns=["Entity2","Comment"])
    df_splitname["Entity"] = ent_uniq
    df_splitname.Entity2 = df_splitname.Entity2.str.strip()
    df_splitname.Comment = df_splitname.Comment.str.strip()

    df_corr = df_owid_roser.merge(df_splitname, how='left', on='Entity')
    assert df_corr.shape[0] == df_owid_roser.shape[0]

    df_owid_roser = df_corr
    del df_corr

    # some corrections for merging
    df_owid_roser.loc[df_owid_roser["Entity2"]=="Czech Republic", "Entity2"] = "Czechia"
    df_owid_roser = df_owid_roser[df_owid_roser.Entity2 != "Rwanda"]
    # subset of columns
    df_owid_roser = df_owid_roser[["Entity2","Date","Cumulative total", "Entity"]]

    # create index
    #print(df_owid_roser.set_index("Entity2").loc["United Kingdom"])
    df_UID = df_owid_roser["Entity2"] + "/" + df_owid_roser.Date.dt.strftime("%Y-%m-%d")
    if df_UID.duplicated().any():
      dup_list = df_owid_roser[df_UID.duplicated()].Entity2
      dup_list = df_owid_roser.set_index("Entity2").loc[dup_list].Entity.unique()[:5]
      raise Exception("UID not unique, eg %s"%(", ".join(dup_list)))

    del df_owid_roser["Entity"]

    # read frozen data
    # This doesnt download and doesnt save to csv again since it's a frozen version
    #df_freeze = self._get_owid_roser_freeze_20200420()
    #
    # append frozen
    #df_owid_roser = pd.concat([df_owid_roser, df_freeze], axis=0, ignore_index=True)
    #df_owid_roser = df_owid_roser[~df_owid_roser[["Entity2","Date"]].duplicated()]
    #df_owid_roser.sort_values(["Entity2","Date"], inplace=True)
    #del df_freeze
    #
    # set index and drop some entries
    #df_owid_roser["UID"] = df_UID
    #df_owid_roser.set_index("UID", inplace=True)
    #
    #print(df_owid_roser.loc["Greece/2020-04-16"])
    # (Pdb) df_owid_roser[df_owid_roser.Entity2=="Greece"]
    #df_owid_roser.drop("Greece/2020-04-16", inplace=True)
    #
    #df_owid_roser.reset_index(inplace=True)
    #del df_owid_roser["UID"]

    # read file and save to csv
    df_owid_roser.to_csv(join(self.dir_l1a_others, fn_owid_roser), index=False)
    self.df_owid_roser_live = df_owid_roser


  def get_owid_ortiz(self):
    """### ourworldindata.org Ortiz page"""

    fn_owid_ortiz = "multiple-ourworldindata.org page 1 ortiz - v20200406.csv"
    df_owid_ortiz = pd.read_csv(join(self.dir_l1a_others, fn_owid_ortiz))

    df_owid_ortiz.Date = pd.to_datetime(df_owid_ortiz.Date)
    # No need # df_owid_ortiz["Source Date"] = pd.to_datetime(df_owid_ortiz["Source Date"])

    df_owid_ortiz.loc[df_owid_ortiz["Country or territory"]=="Czech Republic", "Country or territory"] = "Czechia"


    # skip these entries as well
    # Setting a multi-index is not working for overwriting the Total tests value with NaN
    # (Gives weird error that key 2020-03-19 is not found)
    # Using my own single-index instead
    #df_owid_ortiz.set_index(["Country or territory","Date"], inplace=True)

    df_owid_ortiz["UID"] = df_owid_ortiz["Country or territory"] + "/" + df_owid_ortiz.Date.dt.strftime("%Y-%m-%d")
    if df_owid_ortiz["UID"].duplicated().any(): raise Exception("UID not unique")
    df_owid_ortiz.set_index("UID", inplace=True)
    df_owid_ortiz.loc["Japan/2020-03-19","Total tests"] = np.NaN
    df_owid_ortiz.loc["Ukraine/2020-03-20","Total tests"] = np.NaN
    df_owid_ortiz.loc["Spain/2020-03-18","Total tests"] = np.NaN
    df_owid_ortiz.loc["Canada – Quebec/2020-03-19","Total tests"] = np.NaN

    df_owid_ortiz.reset_index(inplace=True)
    del df_owid_ortiz["UID"]

    self.df_owid_ortiz = df_owid_ortiz


  def get_covidtracking_usa(self):
    fn_covusa_save = join(self.dir_l1a_others, "covidtracking.com-distilled.csv")

    if not self.do_download:
      self.df_covusa = pd.read_csv(fn_covusa_save)
      self.df_covusa["date"] = pd.to_datetime(self.df_covusa.date)
      return

    fn_covusa_daily = join(self.dir_temp, "covidtracking.com-states_daily.csv")
    fn_covusa_info  = join(self.dir_temp, "covidtracking.com-states_info.csv" )
    url_daily = "https://covidtracking.com/api/v1/states/daily.csv"
    url_info  = "https://covidtracking.com/api/v1/states/info.csv"
    #urllib.request.urlretrieve(url_daily, fn_covusa_daily)
    #urllib.request.urlretrieve(url_info , fn_covusa_info)
    my_download(url_daily, fn_covusa_daily, "cov usa daily")
    my_download(url_info, fn_covusa_info, "cov usa info")
    
    df_daily = pd.read_csv(fn_covusa_daily)
    df_info  = pd.read_csv(fn_covusa_info )
    
    df_daily = df_daily.merge(df_info[["state","name"]], how='left', on='state')
    df_daily.date = pd.to_datetime(df_daily.date, format="%Y%m%d")
    df_daily = df_daily[["name","date","positive","negative"]]
    df_daily.sort_values(["name","date"], inplace=True)
    
    # some postprocessing
    df_daily["total_cumul"] = df_daily.positive + df_daily.negative

    # some renames to match with JHU
    df_daily.loc[df_daily.name=="District Of Columbia", "name"] = "District of Columbia"
    df_daily.loc[df_daily.name=="US Virgin Islands", "name"] = "Virgin Islands"

    # Use "US" prefix to match with kaggle confirmed cases convention
    df_daily["name"] = "US – " + df_daily.name

    # drop na
    df_daily = df_daily[pd.notnull(df_daily.total_cumul)]
    
    #drop a dip in total tests
    df_daily["UID"] = df_daily["name"] + "/" + df_daily["date"].dt.strftime("%Y-%m-%d")
    if df_daily["UID"].duplicated().any(): raise Exception("UID not unique")
    df_daily.set_index("UID", inplace=True)

    df_daily.loc["US – West Virginia/2020-04-27", "total_cumul"] = np.NaN
    df_daily.loc["US – Virginia/2020-05-02", "total_cumul"] = np.NaN
    # 
    df_daily.reset_index(inplace=True)
    del df_daily["UID"]
    # save
    df_daily.to_csv(fn_covusa_save, index=False)

    self.df_covusa = df_daily
 


  def get_wikipedia(self):
    """### Wikipedia article, historied"""

    # Update 2020-04-09: start using version from git repo
    # (Shadi to copy Halim's file from gdrive to git repo and commit then upload back to gdrive)
    # fn_wiki = "multiple-Wikipedia_covid19_TotalTests_Table-20200406b.csv"
    fn_wiki = "multiple-Wikipedia_covid19_TotalTests_Table-gitrepo.csv"
    df_wiki = pd.read_csv(join(self.dir_l1a_others, fn_wiki))

    # check if numeric fields are actually numeric
    if df_wiki["Cumulative Test Nb"].dtypes != float:
      # try to cast to float. This will throw an exception if it fails, eg "ValueError: could not convert string to float: '2,12,350'"
      df_wiki["Cumulative Test Nb"] = df_wiki["Cumulative Test Nb"].astype(float)

    # As of 2020-04-09, this is %Y-%m-%d
    # df_wiki["As of Date"] = pd.to_datetime(df_wiki["As of Date"], format="%d-%m-%y")
    df_wiki["As of Date"] = pd.to_datetime(df_wiki["As of Date"], format="%Y-%m-%d")

    # Just use empty string in place of NA
    df_wiki["Region"] = df_wiki.Region.fillna('')

    # fix this naming
    # idx_cz = (df_wiki["Country"]=="Czech") & pd.isnull(df_wiki["Region"])
    idx_cz = (df_wiki["Country"]=="Czech") & (df_wiki["Region"]=="")
    df_wiki.loc[idx_cz, "Country"] = "Czechia"
    df_wiki.loc[idx_cz, "Region"] = ""

    # skip this entry
    # Update 2020-04-09: should no longer be needed
    idx_cz = (df_wiki["Country"]=="Czech") & (df_wiki["Region"]=="Czechia")
    df_wiki = df_wiki.loc[~idx_cz, ]

    # raise an exception if there are still duplicates
    if df_wiki[["Country","Region","As of Date"]].duplicated().any():
      #raise Exception("Found duplicates in wiki data")
      print("Found duplicates in wiki data")
    else:
      print("No duplicates in wiki data")

    # skip dupes, eg India on 2020-03-25
    df_wiki = df_wiki[~df_wiki[["Country","Region","As of Date"]].duplicated()]

    # skip these entries as well
    # Setting a multi-index is not working for overwriting the Total tests value with NaN
    # (Using ["Austria","","2020-03-01"] returns the data for all dates)
    # Using my own single-index instead
    # df_wiki.set_index(["Country","Region","As of Date"], inplace=True)
    df_wiki["UID"] = df_wiki["Country"] + "/" + df_wiki["Region"] + "/" + df_wiki["As of Date"].dt.strftime("%Y-%m-%d")
    if df_wiki["UID"].duplicated().any(): raise Exception("UID not unique")
    df_wiki.set_index("UID", inplace=True)

    df_wiki.loc["Armenia//2020-04-07",    "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Austria//2020-03-01",    "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Azerbaijan//2020-04-01", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Azerbaijan//2020-04-02", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Azerbaijan//2020-04-03", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Australia/Australian Capital Territory/2020-04-13", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Australia/Australian Capital Territory/2020-04-24", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Australia/Tasmania/2020-04-08", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Bahrain//2020-04-07",    "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Bolivia//2020-03-19",    "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/British Columbia/2020-04-13", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/British Columbia/2020-04-14", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Ontario/2020-03-23", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Ontario/2020-03-27", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Prince Edward Island/2020-04-04", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Quebec/2020-03-19",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Quebec/2020-03-21",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Quebec/2020-04-02",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Quebec/2020-04-24",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Croatia//2020-03-01",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Denmark//2020-03-22",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Denmark//2020-03-26",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Denmark//2020-03-28",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["France//2020-04-19",  "Cumulative Test Nb"] = np.NaN

    df_wiki.loc["Germany//2020-03-26",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Germany//2020-04-05",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Germany//2020-04-15",  "Cumulative Test Nb"] = np.NaN

    df_wiki.loc["Greece//2020-04-07",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan//2020-03-01",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan//2020-03-19",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan/Tokyo/2020-03-23", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Kazakhstan//2020-04-05", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-01",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-05",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-09",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-12",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-21",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-26",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-28",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-31",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-04-02",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-04-16",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-04-19",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-04-20",  "Cumulative Test Nb"] = np.NaN

    df_wiki.loc["Russia//2020-03-20",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Spain//2020-03-18",  "Cumulative Test Nb"] = np.NaN # this was 30k, but it's very out of line wtih the 300k on 03-21, so dropping it
    df_wiki.loc["Taiwan//2020-03-19",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["US/California/2020-03-30",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["US/California/2020-03-31",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Ukraine//2020-03-20",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Ukraine//2020-04-01",  "Cumulative Test Nb"] = np.NaN

    df_wiki.loc["Netherlands//2020-04-20",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Netherlands//2020-04-13",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Netherlands//2020-04-06",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Denmark//2020-03-24",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Slovenia//2020-03-01",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["North Korea//2020-04-22",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Belgium//2020-04-30",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Portugal//2020-04-30",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["South Korea//2020-05-02",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan//2020-05-01",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan//2020-05-02",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Netherlands//2020-05-02",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada//2020-05-02",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan//2020-05-03",  "Cumulative Test Nb"] = np.NaN
    df_wiki.reset_index(inplace=True)
    del df_wiki["UID"]

    # drop nan entries
    df_wiki = df_wiki[pd.notnull(df_wiki.Country)]

    self.df_wiki = df_wiki


  def get_worldometers(self):
    """### worldometers.info"""

    # This file's name is 0403 till 0406 but it really contains till 0429
    fn_worldometers = "multiple-worldometers.info-coronavirus-20200403 till 0406.csv"

    # after updating till 2020-04-29, there are some non-utf-8 characters, so using latin1 (synonym of iso... below)
    # http://stackoverflow.com/questions/18171739/ddg#18172249
    df_worldometers = pd.read_csv(join(self.dir_l1a_others, fn_worldometers), encoding = "ISO-8859-1")

    df_worldometers.columns = [x.replace("\n"," ") for x in df_worldometers.columns.tolist()]
    df_worldometers.Date = pd.to_datetime(df_worldometers.Date)

    # if accidentally someone inserts a thousands comma separator in the total tests field, eg "3,123"
    if df_worldometers["Total Tests"].dtypes == object:
      df_worldometers["Total Tests"] = df_worldometers["Total Tests"].str.replace(",","").astype(float)

    # drop their extended points
    df_worldometers = df_worldometers[["Country, Other", "Total Tests", "Date"]].copy()
    df_worldometers.sort_values(["Country, Other", "Date"], inplace=True)
    df_worldometers = df_worldometers[pd.notnull(df_worldometers["Total Tests"])]
    df_worldometers["diffval"] = df_worldometers.groupby("Country, Other")["Total Tests"].apply(lambda s: s.diff())
    df_worldometers = df_worldometers[df_worldometers.diffval.apply(pd.isnull) | (df_worldometers.diffval!=0)]
    del df_worldometers["diffval"]


    # some name corrections
    df_worldometers.loc[df_worldometers["Country, Other"]=="S. Korea", "Country, Other"] = "South Korea"
    df_worldometers.loc[df_worldometers["Country, Other"]=="UK", "Country, Other"] = "United Kingdom"

    # added the below with halim after he updated the worldometers csv file till apr 29
    df_worldometers.loc[df_worldometers["Country, Other"]=="Anguilla", "Country, Other"] = "United Kingdom – Anguilla"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Aruba", "Country, Other"] = "Netherlands – Aruba"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Brunei ", "Country, Other"] = "Brunei" # drop space
    df_worldometers.loc[df_worldometers["Country, Other"]=="Bermuda", "Country, Other"] = "United Kingdom – Bermuda"
    df_worldometers.loc[df_worldometers["Country, Other"]=="British Virgin Islands", "Country, Other"] = "United Kingdom – British Virgin Islands"
    df_worldometers.loc[df_worldometers["Country, Other"]=="CAR", "Country, Other"] = "Central African Republic"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Cayman Islands", "Country, Other"] = "United Kingdom – Cayman Islands"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Channel Islands", "Country, Other"] = "United Kingdom – Channel Islands"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Congo", "Country, Other"] = "Congo (Brazzaville)"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Curaçao", "Country, Other"] = "Netherlands – Curacao"
    df_worldometers.loc[df_worldometers["Country, Other"]=="DRC", "Country, Other"] = "Congo (Kinshasa)"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Faeroe Islands", "Country, Other"] = "Denmark – Faroe Islands"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Falkland Islands", "Country, Other"] = "United Kingdom – Falkland Islands (Malvinas)"
    df_worldometers.loc[df_worldometers["Country, Other"]=="French Guiana", "Country, Other"] = "France – French Guiana"
    df_worldometers.loc[df_worldometers["Country, Other"]=="French Polynesia", "Country, Other"] = "France – French Polynesia "
    df_worldometers.loc[df_worldometers["Country, Other"]=="Gibraltar", "Country, Other"] = "United Kingdom – Gibraltar"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Greenland", "Country, Other"] = "Denmark – Greenland"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Guadeloupe", "Country, Other"] = "France – Guadeloupe"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Guadeloupe", "Country, Other"] = "France – Guadeloupe"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Hong Kong", "Country, Other"] = "China – Hong Kong"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Isle of Man", "Country, Other"] = "United Kingdom Isle of Man"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Ivory Coast", "Country, Other"] = "Cote d'Ivoire"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Mayotte", "Country, Other"] = "France – Mayotte"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Martinique", "Country, Other"] = "France – Martinique"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Montserrat", "Country, Other"] = "United Kingdom – Montserrat"
    df_worldometers.loc[df_worldometers["Country, Other"]=="New Caledonia", "Country, Other"] = "France – New Caledonia"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Palestine", "Country, Other"] = "West Bank and Gaza"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Réunion", "Country, Other"] = "France – Reunion"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Saint Martin", "Country, Other"] = "France – St Martin"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Saint Pierre Miquelon", "Country, Other"] = "France – Saint Pierre and Miquelon"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Sint Maarten", "Country, Other"] = "Netherlands – Sint Maarten"
    df_worldometers.loc[df_worldometers["Country, Other"]=="St. Barth", "Country, Other"] = "France – Saint Barthelemy"
    df_worldometers.loc[df_worldometers["Country, Other"]=="St. Vincent Grenadines", "Country, Other"] = "Saint Vincent and the Grenadines"
    df_worldometers.loc[df_worldometers["Country, Other"]=="Turks and Caicos", "Country, Other"] = "United Kingdom – Turks and Caicos Islands"
    df_worldometers.loc[df_worldometers["Country, Other"]=="UAE", "Country, Other"] = "United Arab Emirates"

    # previous usages of multi-index didn't work, so going ahead with my own single-index
    # df_worldometers.set_index(["Country, Other","Date"], inplace=True)
    df_worldometers["UID"] = df_worldometers["Country, Other"] + "/" + df_worldometers["Date"].dt.strftime("%Y-%m-%d")
    if df_worldometers["UID"].duplicated().any(): raise Exception("UID not unique")
    df_worldometers.set_index("UID", inplace=True)

    # drop these entries
    # TODO replace np.nan overwrite with .drop(...) and just remove the row altogether
    df_worldometers.loc["Argentina/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Argentina/2020-04-05", "Total Tests"] = np.NaN
    df_worldometers.loc["Argentina/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Armenia/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["China – Hong Kong/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["France – St Martin/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Germany/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Germany/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["India/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["India/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Jordan/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Kazakhstan/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Kazakhstan/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Mexico/2020-04-05", "Total Tests"] = np.NaN
    df_worldometers.loc["North Macedonia/2020-04-05", "Total Tests"] = np.NaN
    df_worldometers.loc["North Macedonia/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Philippines/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Spain/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Spain/2020-04-05", "Total Tests"] = np.NaN
    df_worldometers.loc["Spain/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Rwanda/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Cyprus/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Russia/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Belgium/2020-04-29", "Total Tests"] = np.NaN
    df_worldometers.loc["Israel/2020-04-30", "Total Tests"] = np.NaN
    df_worldometers.loc["Cuba/2020-04-30", "Total Tests"] = np.NaN
    df_worldometers.loc["Tunisia/2020-04-29", "Total Tests"] = np.NaN
    df_worldometers.loc["Paraguay/2020-04-30", "Total Tests"] = np.NaN
    df_worldometers.loc["Myanmar/2020-04-30", "Total Tests"] = np.NaN
    df_worldometers.loc["Netherlands/2020-04-07", "Total Tests"] = np.NaN
    df_worldometers.loc["Netherlands/2020-04-13", "Total Tests"] = np.NaN
    df_worldometers.loc["Netherlands/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Belgium/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Belgium/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Rwanda/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Portugal/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Portugal/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Cyprus/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Cyprus/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Denmark/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Denmark/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Czechia/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Finland/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Slovenia/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Georgia/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Georgia/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Estonia/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Tunisia/2020-04-30", "Total Tests"] = np.NaN
    df_worldometers.loc["Croatia/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Iceland/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Afghanistan/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Afghanistan/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Paraguay/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Japan/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Japan/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Finland/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Israel/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Cuba/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["Tunisia/2020-05-01", "Total Tests"] = np.NaN
    df_worldometers.loc["North Macedonia/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Spain/2020-04-29", "Total Tests"] = np.NaN
    df_worldometers.loc["Denmark/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Cuba/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Dominican Republic/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Tunisia/2020-05-02", "Total Tests"] = np.NaN
    df_worldometers.loc["Zambia/2020-05-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Slovenia/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["North Macedonia/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Denmark/2020-05-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Belgium/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Ecuador/2020-05-03", "Total Tests"] = np.NaN
    df_worldometers.loc["Japan/2020-05-03", "Total Tests"] = np.NaN
    
    
    
    # 
    df_worldometers.reset_index(inplace=True)
    del df_worldometers["UID"]

    # drop nan
    df_worldometers = df_worldometers[pd.notnull(df_worldometers["Country, Other"])]

    self.df_worldometers = df_worldometers
   
  def get_uk_channel_jersey(self):
    #UK- Channel Islands Jersey
    url = 'https://opendata.gov.je/api/3/action/datastore_search?resource_id=85a4f87a-49f0-4ef0-b4db-731acdee94bb'  
    fileobj = urllib.request.urlopen(url)
    df=json.loads(fileobj.read())
    df_jersey=pd.DataFrame(columns=["Country","Date","total_cumul"])
    for i in range(0,len(df["result"]["records"])):
        if isinstance(df["result"]["records"][i]["Totalpeopletested"],int):
            row_df=pd.Series(["United Kingdom – Channel Islands",pd.to_datetime(df["result"]["records"][i]["Date"].split("T")[0]),df["result"]["records"][i]["Totalpeopletested"]], index=df_jersey.columns)
            df_jersey=df_jersey.append(row_df, ignore_index=True)
    
    self.df_jersey = df_jersey
    
  def get_biominers(self):
    """### Biominers
    
    Get the csv file from:
    - Export the notion tables with notebook `t11` to the file `multiple-biominers-gitrepo.csv`
    - save into the git repo `covid19-data`
    - commit and upload file to gdrive
    """
    # Start using the git-repo version
    # fn_biominers = "multiple-biominers-v20200406b.csv"
    fn_biominers = "multiple-biominers-gitrepo.csv"
    
    df_biominers = pd.read_csv(join(self.dir_l0_notion, fn_biominers))
    
    df_biominers.Date = pd.to_datetime(df_biominers.Date)

    self.df_biominers = df_biominers



  def merge_all(self):
    """## Merging ourworldindata.org with Wikipedia with worldometers.info"""
    
    #df_owid_roser.columns
    #df_owid_ortiz.columns
    #df_wiki.columns
    #df_worldometers.columns
    #df_biominers.columns
    
    # prep
    df_1a = self.df_owid_roser_live.copy()
    df_1a = df_1a.rename(columns={"Entity2": "Location", "Date": "Date", "Cumulative total": "total_cumul.owid_roser"})
    df_1a = df_1a[["Location","Date","total_cumul.owid_roser"]]

    df_1b = self.df_owid_ortiz.copy()
    df_1b = df_1b.rename(columns={"Country or territory": "Location", "Date": "Date", "Total tests": "total_cumul.owid_ortiz"})
    df_1b = df_1b[["Location","Date","total_cumul.owid_ortiz"]]
    
    df_2 = self.df_covusa.copy()
    df_2 = df_2.rename(columns={"name": "Location", "date": "Date", "total_cumul": "total_cumul.covusa"})
    df_2 = df_2[["Location","Date","total_cumul.covusa"]]

    df_3 = self.df_wiki.copy()
    # df_3["Location"] = df_3.apply(lambda r: r.Country if pd.isna(r.Region) else r.Country+' – '+r.Region, axis=1)
    df_3["Location"] = df_3.apply(lambda r: r.Country if r.Region=="" else str(r.Country)+' – '+str(r.Region), axis=1)
    df_3 = df_3.rename(columns={"Location": "Location", "As of Date": "Date", "Cumulative Test Nb": "total_cumul.wiki"})
    df_3 = df_3[["Location","Date","total_cumul.wiki"]]

    df_4 = self.df_worldometers.copy()
    df_4 = df_4.rename(columns={"Country, Other": "Location", "Date": "Date", "Total Tests": "total_cumul.worldometers"})
    df_4 = df_4[["Location","Date","total_cumul.worldometers"]]
    
    df_5 = self.df_biominers.copy()
    df_5 = df_5.rename(columns={"country_t11": "Location", "Date": "Date", "total_cumul": "total_cumul.biominers"})
    df_5 = df_5[["Location","Date","total_cumul.biominers"]]
    
    # merge
    df_merged = df_1a.merge(df_1b, on=["Location","Date"], how='outer'
                   ).merge(df_2, on=["Location","Date"], how='outer'
                   ).merge(df_3, on=["Location","Date"], how='outer'
                   ).merge(df_4, on=["Location","Date"], how='outer'
                   ).merge(df_5, on=["Location","Date"], how='outer'
                   )

    # sort
    df_merged = df_merged.sort_values(['Location','Date'])

    # get drop_entries.csv file (manually dropped points with 
    fn_drop1 = "drop_entries.csv"
    df_drop1 = pd.read_csv(join(self.dir_l0_notion, fn_drop1))
    df_drop1 = df_drop1[["Location", "Date", "source", "drop row"]]

    # get drop_tests_lessthan_confirmed.csv file
    fn_drop2 = "drop_tests_lessthan_confirmed.csv"
    df_drop2 = pd.read_csv(join(self.dir_l0_notion, fn_drop2))
    df_drop2 = df_drop2[["Location", "Date", "source", "drop row"]]

    # get dropped rows from l1 drop_outlaws
    fn_drop3 = "dropped_outlaws_l1.csv"
    df_drop3 = pd.read_csv(join(self.dir_l1b_altogether, fn_drop3))
    df_drop3 = df_drop3.loc[pd.notnull(df_drop3.is_approved)]
    df_drop3 = df_drop3[["Location", "Date", "total_cumul.source"]]
    df_drop3["drop row"] = "d"
    df_drop3.rename(columns={"total_cumul.source": "source"}, inplace=True)
    
    # get dropped rows from l2 drop_outlaws
    fn_drop4 = "dropped_outlaws_l2.csv"
    df_drop4 = pd.read_csv(join(self.dir_l2_withConf, fn_drop4))
    df_drop4 = df_drop4.loc[pd.notnull(df_drop4.is_approved)]
    df_drop4 = df_drop4[["Location", "Date", "total_cumul.source"]]
    df_drop4["drop row"] = "d"
    df_drop4.rename(columns={"total_cumul.source": "source"}, inplace=True)

    # combine drop files
    df_drop1 = pd.concat([df_drop1, df_drop2, df_drop3, df_drop4], axis=0)
    #df_drop1 = pd.concat([df_drop1, df_drop2], axis=0)

    del df_drop2
    del df_drop3
    del df_drop4

    # prep
    df_drop1.Date = pd.to_datetime(df_drop1.Date)
    df_drop1 = df_drop1[df_drop1["drop row"]=="d"]
    df_drop1["source"] = df_drop1["source"].str.replace("covidtracking.com","covusa")
    df_drop1["source"] = df_drop1["source"].str.replace("owid/ortiz","owid_ortiz")
    df_drop1["source"] = df_drop1["source"].str.replace("owid/roser","owid_roser")
    df_drop1["source"] = "total_cumul."+df_drop1["source"]

    # go to long format
    dfm_long = pd.melt(df_merged, id_vars=['Location','Date'], value_vars=['total_cumul.owid_roser', 'total_cumul.owid_ortiz', 'total_cumul.covusa', 'total_cumul.wiki', 'total_cumul.worldometers', 'total_cumul.biominers']).rename(columns={"variable":"source"})
    dfm_long.sort_values(["Location", "Date", "source"], inplace=True)

    # drop entries from df_drop1
    dfm_long = dfm_long.merge(df_drop1[['Location','Date','source','drop row']], on=['Location','Date','source'], how='left')
    dfm_long = dfm_long[pd.isnull(dfm_long["drop row"])]
    del dfm_long["drop row"]

    # sort
    dfm_long = dfm_long.sort_values(['Location','Date','source'])

    if dfm_long[['Location','Date','source']].duplicated().any():
      print(dfm_long[dfm_long[['Location','Date','source']].duplicated()].head())
      raise Exception("Duplicates in merged altogether data. Above is top 5 examples")

    dfm_wide = dfm_long.set_index(['Location','Date','source']).unstack('source')
    dfm_wide = dfm_wide.xs('value', axis=1, drop_level=True)
    dfm_wide.reset_index(inplace=True)
    dfm_wide = dfm_wide[['Location', 'Date', 'total_cumul.owid_roser', 'total_cumul.owid_ortiz', 'total_cumul.covusa', 'total_cumul.wiki', 'total_cumul.worldometers', 'total_cumul.biominers']]

    # save to class
    self.df_merged = dfm_wide


  def aggregate_and_to_csv(self):
    """## Aggregate for a bird's eye view"""
    
    # df_agg = df_merged.groupby("Location").Date.agg([np.min,np.max,len])
    
    df_agg = self.df_merged.groupby("Location").agg(
                                      {"Date": [np.min,np.max,len],
                                       "total_cumul.owid_roser": lambda x: sum(pd.notnull(x)),
                                       "total_cumul.owid_ortiz": lambda x: sum(pd.notnull(x)),
                                       "total_cumul.covusa": lambda x: sum(pd.notnull(x)),
                                       "total_cumul.wiki": lambda x: sum(pd.notnull(x)),
                                       "total_cumul.worldometers": lambda x: sum(pd.notnull(x)),
                                       "total_cumul.biominers": lambda x: sum(pd.notnull(x)),
                                       })
    # df_agg.columns = ["dt_min", "dt_max", "len.owid_roser", "len.owid_ortiz", "len.wiki", "len.worldometers"]
    
    # df_agg.reset_index().columns
    
    # df_agg.head(30) # value_counts()
    # df_agg.loc["Lebanon"]
    # df_agg.loc["Austria"]
    # df_agg.loc["Afghanistan"]
    #df_agg.loc["South Korea"]
    
    # raise Exception("uncomment to overwrite")
    # fn_analysis_agg = "multiple-analysis_of_aggregated_owid_wiki_worldometers-v20200406.csv"
    # fn_analysis_agg = "multiple-analysis_of_aggregated_owid_wiki_worldometers-v20200406b.csv"
    fn_analysis_agg = "multiple-analysis_of_aggregated_owid_wiki_worldometers-v20200406c.csv"
    df_agg.to_csv(join(self.dir_l1b_altogether, fn_analysis_agg))


  def one_field(self):
    """## Combine into a single dataset"""
    df_merged = self.df_merged
    
    # if the sequence of priorities is changed, change in this part and the part below
    df_merged["total_cumul.all"] = df_merged["total_cumul.owid_roser"].fillna(
                                   df_merged["total_cumul.owid_ortiz"].fillna(
                                   df_merged["total_cumul.covusa"].fillna(
                                   df_merged["total_cumul.biominers"].fillna(
                                   df_merged["total_cumul.wiki"].fillna(
                                   df_merged["total_cumul.worldometers"]
                                   )
                                   )
                                   )
                                   )
                                   )
    # if the sequence of priorities is changed, change in this part and the part above
    df_merged["total_cumul.source"] = df_merged.apply(lambda r:
                                        "owid/roser" if pd.notnull(r["total_cumul.owid_roser"])
                                        else "owid/ortiz" if pd.notnull(r["total_cumul.owid_ortiz"])
                                        else "covidtracking.com" if pd.notnull(r["total_cumul.covusa"])
                                        else "biominers" if pd.notnull(r["total_cumul.biominers"])
                                        else "wiki" if pd.notnull(r["total_cumul.wiki"])
                                        else "worldometers" if pd.notnull(r["total_cumul.worldometers"])
                                        else np.NaN,
                                        axis=1
                                      )

    # drop dates where we couldn't select anything
    # This happens if we originally had data but it got dropped
    df_merged = df_merged[pd.notnull(df_merged["total_cumul.source"])]

    # sort
    df_merged = df_merged.sort_values(["Location","Date"], ascending=True)

    self.df_merged = df_merged


  def drop_outlaws(self):
    fn_wrong = join(self.dir_l1b_altogether, "dropped_outlaws_l1.csv")

    df_merged = self.df_merged.copy()

    # identify dips in the number of tests, supposedly cumulative
    # Also identify country/state/date triplets where the number of tests < number of confirmed cases
    df_merged["daily_test"] = df_merged.groupby("Location")["total_cumul.all"].apply(lambda g: g.fillna(method="ffill").diff()).fillna(0)
    #df_merged["UID"] = df_merged.Location + '/' + df_merged.Date.dt.strftime("%Y-%m-%d")

    # append starting date per Location
    #dt_min = df_merged[["Location","Date"]].groupby("Location").Date.min().reset_index().rename(columns={"Date": "dt_min"})
    #df_merged = df_merged.merge(dt_min, how="left", on="Location")

    #df_wrong = df_merged[pd.notnull(df_merged["total_cumul.all"])].copy()
    #df_wrong["daily_test"] = df_wrong.groupby("Location")["total_cumul.all"].diff()
    # Mark negative daily tests or daily=0 from wiki or worldometers
    # Update: allow daily=0 as this will be cleaned up in the comparison with confirmed cases, i.e. if there was at least 1 new confirmed case, then it's not possible to have 0 new tests.
    loc_wrong = (df_merged.daily_test < 0)
    #loc_zer = ((df_merged.daily_test==0) & (df_merged["total_cumul.source"].isin(["wikipedia","worldometers"]))) & (df_merged.Date != df_merged.dt_min)
    # df_wrong = loc_neg | loc_zer
    if not loc_wrong.any():
      # just clean the csv from the context entries
      df_old = pd.read_csv(fn_wrong)
      df_old["Date"] = pd.to_datetime(df_old.Date)
      df_old = df_old.sort_values(["Location", "Date", "total_cumul.source"])
      df_old = df_old.loc[pd.notnull(df_old.is_approved)]
      df_old.to_csv(fn_wrong, index=False)
      return

    df_merged["is_wrong"] = False
    df_merged.loc[loc_wrong, "is_wrong"] = True

    loc_context = add_context_to_bool_loc(df_merged, "Location", "is_wrong", 10)

    df_merged["is_approved"] = False
    df_merged.loc[loc_wrong & (df_merged["total_cumul.source"]=="worldometers"), "is_approved"] = True

    no_work_required = df_merged.loc[loc_wrong].is_approved.all()

    df_merged = df_merged[["Location", "Date", "total_cumul.source", "total_cumul.all", "is_wrong", "is_approved"]]

    print("Found %i triplets with dips in their cumulative tests. Here are the top 20:"%loc_wrong.sum())
    print(df_merged.loc[loc_wrong].head(20))

    # save wrong values into separate csv
    df_merged["is_wrong"] = df_merged.is_wrong.map(lambda x: "x" if x else "")
    df_merged["is_approved"] = df_merged.is_approved.map(lambda x: "x" if x else "")

    df_context = df_merged.loc[loc_context]

    df_old = pd.read_csv(fn_wrong)
    df_old["Date"] = pd.to_datetime(df_old.Date)

    #df_new = pd.concat([df_context, df_old], axis=0)
    df_new = df_context.merge(df_old, how="outer", on=["Location","Date","total_cumul.source"], suffixes=["","_old"])
    for fx in ["total_cumul.all", "is_wrong", "is_approved"]:
      df_new[fx] = df_new[fx].fillna(df_new[fx+"_old"])
      del df_new[fx+"_old"]

    df_new = df_new.sort_values(["Location", "Date", "total_cumul.source"])
    df_new = df_new.loc[~df_new.duplicated()]
    #import os
    #df_new.to_csv(fn_wrong, index=False, mode='a', header=not os.path.isfile(fn_wrong), sep="\t")
    df_new.to_csv(fn_wrong, index=False)

    # Note: need to re-run rather than just overwrite these values with nan so that the next-best source can provide the number
    #       Also, some cases are not easy to automate and require human judgement
    import click
    if no_work_required:
      msg = """
      WARNING: added new entries to drop in l1b-altogether/dropped_outlaws_l1.csv ,
               but all were marked as approved automatically because it is all from worldometers data.
               Just re-run l1.
      """
      click.secho(msg, fg="yellow")
    else:
      msg = """
      WARNING: Please mark approved (or fix) in l1b-altogether/dropped_outlaws_l1.csv then re-run l1 to re-calculate selected source per country/state/date triplet
      Hint: by default, we mark worldometers drops as approved
      """
      click.secho(msg, fg="red")

    import sys
    sys.exit(1)


  def to_csv_subcols(self):
    # save
    #raise Exception("uncomment to overwrite")
    #fn_agg = "multiple-aggregated_owid_wiki_worldometers_biominers-v20200406.csv"
    #fn_agg = "multiple-aggregated_owid_wiki_worldometers_biominers-v20200406b.csv"
    # fn_agg = "multiple-aggregated_owid_wiki_worldometers_biominers-v20200406c.csv"
    fn_agg = "multiple-aggregated_owid_wiki_worldometers_biominers-gitrepo.csv"
    
    df_save = self.df_merged[["Location","Date","total_cumul.all","total_cumul.source"]]
    df_save = df_save[pd.notnull(df_save["total_cumul.all"])]
    df_save = df_save.sort_values(["Location","Date"], ascending=True)
    
    df_save.to_csv(join(self.dir_l1b_altogether, fn_agg), index=False)
    
    fn_agg2 = "covid19-testing-dataset.csv"
    df_save.loc[df_save["total_cumul.source"]=="biominers","total_cumul.source"]="lau"
    df_save.to_csv(join(self.dir_l1b_altogether, fn_agg2), index=False)

  def to_csv_all(self):
    # save a 2nd, side-by-side version
    #raise Exception("uncomment to overwrite")
    #fn_agg = "multiple-aggregated_owid_wiki_worldometers_biominers-v20200406b-sidebyside.csv"
    # fn_agg = "multiple-aggregated_owid_wiki_worldometers_biominers-v20200406c-sidebyside.csv"
    fn_agg = "multiple-aggregated_owid_wiki_worldometers_biominers-gitrepo-sidebyside.csv"
    
    # df_save = df_merged[["Location","Date","total_cumul.all","total_cumul.source"]]
    df_save = self.df_merged
    df_save = df_save[pd.notnull(df_save["total_cumul.all"])]
    df_save = df_save.sort_values(["Location","Date"], ascending=True)
    
    df_save.to_csv(join(self.dir_l1b_altogether, fn_agg), index=False)

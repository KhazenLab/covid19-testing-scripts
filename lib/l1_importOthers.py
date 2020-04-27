# -*- coding: utf-8 -*-

from os.path import join
import pandas as pd
import numpy as np
import tempfile
import urllib.request
import json


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
    urllib.request.urlretrieve(url_global, fn_global)
    
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
    urllib.request.urlretrieve(url_globalDeath, fn_globalDeath)
    
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
    urllib.request.urlretrieve(url_usa, fn_usa)
    
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
    urllib.request.urlretrieve(url_USDeath, fn_USDeath)
    
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

  def __init__(self, dir_gdrive):
    self.dir_l0_notion = join(dir_gdrive, "l0-notion_tables")
    self.dir_l1a_others = join(dir_gdrive, "l1a-non-biominer_data")
    self.dir_l1b_altogether = join(dir_gdrive, "l1b-altogether")
    self.dir_temp = tempfile.mkdtemp()
    self.jhu = JhuImporter(dir_gdrive)    


  def get_jhu_conf_deaths(self):
    df_conf_gl = self.jhu.get_jhu_confirmed_global()
    df_conf_us = self.jhu.get_jhu_confirmed_usa()
    df_dead_gl = self.jhu.get_jhu_deaths_global()
    df_dead_us = self.jhu.get_jhu_deaths_usa()

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


  def get_owid_roser_freeze_20200420(self):
    # This doesnt download and doesnt save to csv again since it's a frozen version
    fn_owid_roser = "ourworldindata.org-roser-freeze_20200420.csv"
    df_owid_roser = pd.read_csv(join(self.dir_l1a_others, fn_owid_roser))
    df_owid_roser["Date"] = pd.to_datetime(df_owid_roser.Date)
    self.df_owid_roser_v20200420 = df_owid_roser


  def get_owid_roser_live(self):
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
    csv_url = "https://github.com/owid/covid-19-data/raw/master/public/data/testing/covid-testing-all-observations.csv"
    urllib.request.urlretrieve(csv_url, join(self.dir_temp, fn_owid_roser))

    # Read
    df_owid_roser = pd.read_csv(join(self.dir_temp, fn_owid_roser))
    df_owid_roser.Date = pd.to_datetime(df_owid_roser.Date)

    # Split the name and comment for simplicity
    df_splitname = pd.DataFrame(df_owid_roser.Entity.str.split("-").tolist(), columns=["Entity2","Comment"])
    df_splitname.Entity2 = df_splitname.Entity2.str.strip()
    df_splitname.Comment = df_splitname.Comment.str.strip()

    df_corr = pd.concat([df_owid_roser,
               df_splitname],
              ignore_index=True,
              axis=1
             )
    df_corr.columns = df_owid_roser.columns.tolist() + df_splitname.columns.tolist()

    df_owid_roser = df_corr
    del df_corr

    # some corrections for merging
    df_owid_roser.loc[df_owid_roser["Entity2"]=="Czech Republic", "Entity2"] = "Czechia"

    # subset of columns
    df_owid_roser = df_owid_roser[["Entity2","Date","Cumulative total"]]

    # drop some dupes data, with: India - samples tested, United States - specimens tested (CDC), japan - tests performed, etc
    df_owid_roser = df_owid_roser[df_owid_roser.Entity2 != "India - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity2 != "United States - inconsistent units (COVID Tracking Project)"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity2 != "Japan - people tested"]
    df_owid_roser = df_owid_roser[df_owid_roser.Entity2 != "Singapore - people tested"]

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

    df_owid_ortiz.reset_index(inplace=True)
    del df_owid_ortiz["UID"]

    self.df_owid_ortiz = df_owid_ortiz


  def get_covidtracking_usa(self):
    fn_covusa_daily = join(self.dir_temp, "covidtracking.com-states_daily.csv")
    fn_covusa_info  = join(self.dir_temp, "covidtracking.com-states_info.csv" )
    url_daily = "https://covidtracking.com/api/states/daily.csv"
    url_info  = "https://covidtracking.com/api/states/info.csv"
    urllib.request.urlretrieve(url_daily, fn_covusa_daily)
    urllib.request.urlretrieve(url_info , fn_covusa_info)
    
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

    # save
    fn_covusa_save = join(self.dir_l1a_others, "covidtracking.com-distilled.csv")
    df_daily.to_csv(fn_covusa_save, index=False)

    self.df_covusa = df_daily
 


  def get_wikipedia(self):
    """### Wikipedia article, historied"""

    # Update 2020-04-09: start using version from git repo
    # (Shadi to copy Halim's file from gdrive to git repo and commit then upload back to gdrive)
    # fn_wiki = "multiple-Wikipedia_covid19_TotalTests_Table-20200406b.csv"
    fn_wiki = "multiple-Wikipedia_covid19_TotalTests_Table-gitrepo.csv"
    df_wiki = pd.read_csv(join(self.dir_l1a_others, fn_wiki))

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
    df_wiki.loc["Azerbaijan//2020-04-03", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Bahrain//2020-04-07",    "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Bolivia//2020-03-19",    "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Ontario/2020-03-23", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Ontario/2020-03-27", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Prince Edward Island/2020-04-04", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Quebec/2020-03-21",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Canada/Quebec/2020-04-02",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Greece//2020-04-07",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan//2020-03-01",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan//2020-03-19",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Japan/Tokyo/2020-03-23", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Kazakhstan//2020-04-05", "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-01",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-05",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-09",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-12",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-26",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Philippines//2020-03-28",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Russia//2020-03-20",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Spain//2020-03-18",  "Cumulative Test Nb"] = np.NaN # this was 30k, but it's very out of line wtih the 300k on 03-21, so dropping it
    df_wiki.loc["Taiwan//2020-03-19",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["US/California/2020-03-30",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["US/California/2020-03-31",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Ukraine//2020-03-20",  "Cumulative Test Nb"] = np.NaN
    df_wiki.loc["Ukraine//2020-04-01",  "Cumulative Test Nb"] = np.NaN

    df_wiki.reset_index(inplace=True)
    del df_wiki["UID"]

    self.df_wiki = df_wiki


  def get_worldometers(self):
    """### worldometers.info"""

    fn_worldometers = "multiple-worldometers.info-coronavirus-20200403 till 0406.csv"
    df_worldometers = pd.read_csv(join(self.dir_l1a_others, fn_worldometers))

    df_worldometers.columns = [x.replace("\n"," ") for x in df_worldometers.columns.tolist()]
    df_worldometers.Date = pd.to_datetime(df_worldometers.Date)

    df_worldometers.loc[df_worldometers["Country, Other"]=="S. Korea", "Country, Other"] = "South Korea"
    df_worldometers.loc[df_worldometers["Country, Other"]=="UK", "Country, Other"] = "United Kingdom"

    # previous usages of multi-index didn't work, so going ahead with my own single-index
    # df_worldometers.set_index(["Country, Other","Date"], inplace=True)
    df_worldometers["UID"] = df_worldometers["Country, Other"] + "/" + df_worldometers["Date"].dt.strftime("%Y-%m-%d")
    if df_worldometers["UID"].duplicated().any(): raise Exception("UID not unique")
    df_worldometers.set_index("UID", inplace=True)

    # drop these entries
    df_worldometers.loc["Argentina/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Argentina/2020-04-05", "Total Tests"] = np.NaN
    df_worldometers.loc["Argentina/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Armenia/2020-04-04", "Total Tests"] = np.NaN
    df_worldometers.loc["Germany/2020-04-06", "Total Tests"] = np.NaN
    df_worldometers.loc["Hong Kong/2020-04-04", "Total Tests"] = np.NaN
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
    
    # 
    df_worldometers.reset_index(inplace=True)
    del df_worldometers["UID"]

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
    
    df_1c = self.df_owid_roser_v20200420.copy()
    df_1c = df_1c.rename(columns={"Entity2": "Location", "Date": "Date", "Cumulative total": "total_cumul.owid_roser"})
    df_1c = df_1c[["Location","Date","total_cumul.owid_roser"]]

    # FIXME temporarily merge df_1a and df_1c to get a clean git diff in data repo
    df_1a = pd.concat([df_1a, df_1c], axis=0)
    df_1a = df_1a[~df_1a[["Location","Date"]].duplicated()]
    del df_1c

    # prep others 
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
    self.df_merged = df_merged


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

    # check that there are no dips in the data, eg mixing different sources with one being lagged
    # FIXME should do something about these
    country_dipped = df_merged.groupby("Location")["total_cumul.all"].apply(lambda g: g.diff().min())
    print("Top country dips in total tests:")
    print(country_dipped.sort_values(ascending=True).head(20))

    self.df_merged = df_merged



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

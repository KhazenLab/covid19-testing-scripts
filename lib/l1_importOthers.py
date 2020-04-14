# -*- coding: utf-8 -*-

from os.path import join
import pandas as pd
import numpy as np


class L1ImportOthers:

  def __init__(self, dir_gdrive):
    self.dir_gdrive = dir_gdrive


  def get_owid_roser(self):
    """
    Download the data from ourworldindata.org that is referenced at
    https://ourworldindata.org/coronavirus#the-total-number-of-tests-performed-or-people-tested-so-far

    Update 2020-04-14:
    Replace their csv from the ourworldindata.org article (download from plot) with the one from the github repo. It contains more dates/countries
    """

    #fn_owid_roser = "multiple-ourworldindata.org page 2 roser - v20200406.csv"
    fn_owid_roser = "multiple-ourworldindata.org page 2 roser - gitub.csv"

    # download file
    import urllib.request
    csv_url = "https://github.com/owid/covid-19-data/raw/master/public/data/testing/covid-testing-all-observations.csv"
    urllib.request.urlretrieve(csv_url, join(self.dir_gdrive, fn_owid_roser))

    # Read
    df_owid_roser = pd.read_csv(join(self.dir_gdrive, fn_owid_roser))
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

    self.df_owid_roser = df_owid_roser


  def get_owid_ortiz(self):
    """### ourworldindata.org Ortiz page"""

    fn_owid_ortiz = "multiple-ourworldindata.org page 1 ortiz - v20200406.csv"
    df_owid_ortiz = pd.read_csv(join(self.dir_gdrive, fn_owid_ortiz))

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

    df_owid_ortiz.reset_index(inplace=True)
    del df_owid_ortiz["UID"]

    self.df_owid_ortiz = df_owid_ortiz


  def get_wikipedia(self):
    """### Wikipedia article, historied"""

    # Update 2020-04-09: start using version from git repo
    # (Shadi to copy Halim's file from gdrive to git repo and commit then upload back to gdrive)
    # fn_wiki = "multiple-Wikipedia_covid19_TotalTests_Table-20200406b.csv"
    fn_wiki = "multiple-Wikipedia_covid19_TotalTests_Table-gitrepo.csv"
    df_wiki = pd.read_csv(join(self.dir_gdrive, fn_wiki))

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
    df_worldometers = pd.read_csv(join(self.dir_gdrive, fn_worldometers))

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

    # 
    df_worldometers.reset_index(inplace=True)
    del df_worldometers["UID"]

    self.df_worldometers = df_worldometers



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
    
    df_biominers = pd.read_csv(join(self.dir_gdrive, fn_biominers))
    
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
    df_1 = self.df_owid_roser.copy()
    df_1 = df_1.rename(columns={"Entity2": "Location", "Date": "Date", "Cumulative total": "total_cumul.owid_roser"})
    df_1 = df_1[["Location","Date","total_cumul.owid_roser"]]
    
    df_2 = self.df_owid_ortiz.copy()
    df_2 = df_2.rename(columns={"Country or territory": "Location", "Date": "Date", "Total tests": "total_cumul.owid_ortiz"})
    df_2 = df_2[["Location","Date","total_cumul.owid_ortiz"]]
    
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
    df_merged = df_1.merge(df_2, on=["Location","Date"], how='outer'
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
    df_agg.to_csv(join(self.dir_gdrive, fn_analysis_agg))


  def one_field(self):
    """## Combine into a single dataset"""
    df_merged = self.df_merged
    
    df_merged["total_cumul.all"] = df_merged["total_cumul.owid_roser"].fillna(
                                   df_merged["total_cumul.owid_ortiz"].fillna(
                                     df_merged["total_cumul.wiki"].fillna(
                                       df_merged["total_cumul.worldometers"].fillna(
                                           df_merged["total_cumul.biominers"]
                                       )
                                     )
                                    )
                                    )
    
    df_merged["total_cumul.source"] = df_merged.apply(lambda r:
                                        "owid/roser" if pd.notnull(r["total_cumul.owid_roser"])
                                        else "owid/ortiz" if pd.notnull(r["total_cumul.owid_ortiz"])
                                        else "wiki" if pd.notnull(r["total_cumul.wiki"])
                                        else "worldometers" if pd.notnull(r["total_cumul.worldometers"])
                                        else "biominers" if pd.notnull(r["total_cumul.biominers"])
                                        else np.NaN,
                                        axis=1
                                      )

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
    
    df_save.to_csv(join(self.dir_gdrive, fn_agg), index=False)
    

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
    
    df_save.to_csv(join(self.dir_gdrive, fn_agg), index=False)

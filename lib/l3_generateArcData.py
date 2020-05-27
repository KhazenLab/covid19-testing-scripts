import pandas as pd
import numpy as np
from os.path import join

class L3GenerateArcData:
  """
  Written by Halim
  Class that reads csv file from l2/historical and generates files in l3_arcgis for display on the dashboard
  """
  def __init__(self, dir_gitrepo):
    self.dir_l2_withConf = join(dir_gitrepo, "l2-withConfirmed")
    self.dir_l3_arcgis = join(dir_gitrepo, "ArcGIS")

  def read_l2_historical(self):
    historicalData=pd.read_csv(join(self.dir_l2_withConf, 't11c-confirmed+totalTests-historical.csv'), delimiter=',')
    historicalData['CountryProv']=historicalData['CountryProv'].str.replace("[*]","")

    historicalData['Updated']=""
    historicalData['Interpolated']="No"
    self.historicalData = historicalData


  def calculate_stats(self):
    historicalData = self.historicalData

    self.countries = historicalData['CountryProv'].unique()

    for country in self.countries:
    
        indexHist= np.where(historicalData.CountryProv==country)
        countryData=historicalData.iloc[indexHist].copy()
        tests=countryData['total_cumul.all']
        
        if sum(tests.notna())==0:
            continue

        # add 1 since R is 1-based and py is 0-based
        indexfin=np.amax(np.where((tests.notna()))) + 1
        isUpdated = (indexfin==len(tests)) or (indexfin==(len(tests)-1))
    
        # forward-fill the last NA for the sake of visualization
        dailyConfirmed=countryData["ConfirmedCases"].diff()
        tests.iloc[indexfin-1:] = tests.iloc[indexfin-1:].fillna(method="ffill")
        countryData.iloc[indexfin:, 'total_cumul.all'==countryData.columns] = tests.iloc[indexfin:]+dailyConfirmed[indexfin:]
        countryData.iloc[indexfin:, 'Interpolated'==countryData.columns]="Yes"
        
        #countryData['total_cumul.all']=countryData['total_cumul.all'].interpolate()
        
        #interpolate using method7
        tests=countryData["total_cumul.all"].copy()
        tests2=countryData["total_cumul.all"].copy()
        interpolated=countryData["Interpolated"].copy()
        confirmed=countryData["ConfirmedCases"].copy()
        indexMinNonNA= tests.iloc[(np.where((tests.notna())))[0]].index.min()
        indexNAafterFirstNb = tests.iloc[np.where((tests.isna() & (tests.index>indexMinNonNA)))[0]].index


        if len(indexNAafterFirstNb)>0:
            for indexCurrent in indexNAafterFirstNb:
              
              indexNbBefore= tests.iloc[(np.where((tests.notna() & (tests.index<indexCurrent))))[0]].index.max()
              indexNbAfter= tests.iloc[(np.where((tests.notna() & (tests.index>indexCurrent))))[0]].index.min()
              if tests[indexNbAfter]==tests[indexNbBefore]:
                tests2[indexCurrent]=tests[indexNbBefore]
                continue
              if tests[indexNbAfter]<tests[indexNbBefore]:
                raise Exception("This function is only for increasing cumulative vec_with_na, check country:"+country +", testNbAfter:"+str(tests[indexNbAfter])+", testNbBefore"+str(tests[indexNbBefore]))
              translateFirst=tests[indexNbBefore]-confirmed[indexNbBefore]
              scaleLast=(tests[indexNbAfter]-(confirmed[indexNbAfter]+translateFirst))/(confirmed[indexNbAfter]+translateFirst)
              interpolated[indexCurrent]="Yes"
              tests2[indexCurrent]=(confirmed[indexCurrent]+translateFirst)*(1+scaleLast*((indexCurrent-indexNbBefore)/(indexNbAfter-indexNbBefore)))
              tests2[indexCurrent]=np.floor(tests2[indexCurrent])
        
        countryData["total_cumul.all"].update(tests2)
        countryData["Interpolated"].update(interpolated)
        countryData['Updated']="*" if isUpdated else ""
    
        historicalData.update(countryData)

    # round after the interpolation
    historicalData['total_cumul.all']=np.round(historicalData['total_cumul.all'],0)
 
    # more stats
    historicalData['tests_per_mil']=np.floor(historicalData['total_cumul.all']*1000000/historicalData['Population'])
    historicalData['ratio_confirmed_total_pct']=historicalData['ConfirmedCases']*100/historicalData['total_cumul.all']
    historicalData['negative_cases']=historicalData['total_cumul.all']-historicalData['ConfirmedCases']
    historicalData.loc[historicalData["ratio_confirmed_total_pct"]>=100,"ratio_confirmed_total_pct"]=101;
    historicalData["ratio_confirmed_total_pct"]=np.round(historicalData["ratio_confirmed_total_pct"],2)
    historicalData["ratio_confirmed_total_pct"]=historicalData["ratio_confirmed_total_pct"].replace(101,np.nan);
    
  def write_latest(self):
    historicalData = self.historicalData

    indexLatest=np.where(historicalData.Date==max(historicalData.Date))
    selectColumns=historicalData[['CountryProv','Lat','Long','ConfirmedCases','Fatalities','total_cumul.all','negative_cases','tests_per_mil','ratio_confirmed_total_pct','Population','Updated','Interpolated']]
    
    latest=selectColumns.iloc[indexLatest]
    latest = latest.rename(columns={
      "ConfirmedCases": "Max - ConfirmedCases",
      "Fatalities": "Max - Fatalities",
      "total_cumul.all": "Max - total_cumul.all",
      "negative_cases": "Max - negative_cases",
      "tests_per_mil": "Max - tests_per_mil",
      "ratio_confirmed_total_pct": "Max - ratio_confirmed_total_pct",
      "Population": "Max - Population",
    })
    
    # sort column order
    colorder = ["CountryProv", "Lat", "Long",
                "Max - ConfirmedCases", "Max - Fatalities", "Max - total_cumul.all",
                "Max - Population", "Max - tests_per_mil", "Max - ratio_confirmed_total_pct",
                "Max - negative_cases", "Updated","Interpolated"]
    latest = latest[colorder]

    #save latest to csv
    latest.to_csv(join(self.dir_l3_arcgis, 'v2', 't11c-confirmedtotalTests-latestOnly.csv'), index=False)


  def write_dailyStacked(self):
    historicalData = self.historicalData

    dailyConfirmed=pd.Series([])
    dailyNegative=pd.Series([])
    dailyTests=pd.Series([])
    for country in self.countries:
      indexHist= np.where(historicalData.CountryProv==country)
      countryData=historicalData.iloc[indexHist]
      confirmed=[0]
      confirmed[1:] = countryData['ConfirmedCases']
      confirmed=pd.Series(confirmed)
      dailyConfirmed=pd.concat([dailyConfirmed,pd.Series(np.diff(confirmed))], ignore_index=True)
    
      negative=[0]
      negative[1:] = countryData['negative_cases']
      negative=pd.Series(negative)
      dailyNegative=pd.concat([dailyNegative,pd.Series(np.diff(negative))], ignore_index=True)
    
      tests=[0]
      tests[1:] = countryData['total_cumul.all']
      tests=pd.Series(tests)
      dailyTests=pd.concat([dailyTests,pd.Series(np.diff(tests))], ignore_index=True)
      
    
    dailyConfirmed[dailyConfirmed<0]=0;
    dailyNegative[dailyNegative<0]=0;
    dailyTests[dailyTests<0]=0;
    
    date=pd.concat([historicalData['Date'],historicalData['Date']], ignore_index=True)
    historicalData['Negative']="Negative"
    historicalData['Positive']="Positive"
    positiveNegative=pd.concat([historicalData['Positive'],historicalData['Negative']], ignore_index=True)
    daily=pd.concat([dailyConfirmed,dailyNegative], ignore_index=True)
    cumulative=pd.concat([historicalData['ConfirmedCases'],historicalData['negative_cases']], ignore_index=True)
    country=pd.concat([historicalData['CountryProv'],historicalData['CountryProv']], ignore_index=True)
    
    cumulative[cumulative<0]=0;

    data={'CountryProv':country,'Date':date,'dailyValue':daily,'cumulativeValue':cumulative, 'Positive/Negative':positiveNegative} 
    
    stacked=pd.DataFrame(data);

    #Save stacked in stacked csv
    stacked.to_csv(join(self.dir_l3_arcgis, 'v2', 't11c-confirmedtotalTests-historical-stacked.csv'), index=False)

    self.historicalData = historicalData

    # save back into class member
    self.historicalData = historicalData
    dailyConfirmed=pd.concat([dailyConfirmed,pd.Series(np.diff(confirmed))], ignore_index=True)
    
    historicalData["daily_ratio_confirmed_total_pct"]=(dailyConfirmed*100/(dailyConfirmed+dailyNegative))
    historicalData["daily_tests_per_mil"]=(dailyTests*1000000/historicalData['Population'])
    
    historicalData.loc[historicalData["daily_tests_per_mil"]<=0,"daily_tests_per_mil"]=-1;     
    historicalData["daily_tests_per_mil"]=np.round(historicalData["daily_tests_per_mil"],2)
    historicalData["daily_tests_per_mil"]=historicalData["daily_tests_per_mil"].replace(-1,np.nan);
    
    historicalData.loc[historicalData["daily_ratio_confirmed_total_pct"]<0,"daily_ratio_confirmed_total_pct"]=-1;
    historicalData.loc[historicalData["daily_ratio_confirmed_total_pct"]>=100,"daily_ratio_confirmed_total_pct"]=-1;  
    historicalData["daily_ratio_confirmed_total_pct"]=historicalData["daily_ratio_confirmed_total_pct"].replace(-1,np.nan);
    historicalData["daily_ratio_confirmed_total_pct"]=historicalData["daily_ratio_confirmed_total_pct"].replace([np.inf, -np.inf], np.nan)
    historicalData["daily_ratio_confirmed_total_pct"]=np.round(historicalData["daily_ratio_confirmed_total_pct"],2)
    
    historicalData["daily_tests_per_positive"]=np.round(dailyTests/dailyConfirmed,2);
    historicalData["tests_per_positive"]=np.round(historicalData["total_cumul.all"]/historicalData["ConfirmedCases"],2);
    
    historicalData= historicalData[["CountryProv","Date","tests_per_mil","ratio_confirmed_total_pct","daily_ratio_confirmed_total_pct","daily_tests_per_mil","tests_per_positive","daily_tests_per_positive","Interpolated"]]
    historicalData.to_csv(join(self.dir_l3_arcgis, 'v2', 't11c-confirmedtotalTests-historical.csv'), index=False)

  def write_chisquared(self):
    historicalData = self.historicalData

    chiSquareData=pd.read_csv(join(self.dir_l2_withConf, 't11d-chisquared-ranks.csv'))

    data={'CountryProv':historicalData['CountryProv'],'Lat':historicalData['Lat'],'Long':historicalData['Long'],'Updated':historicalData['Updated']}
    lhs=pd.DataFrame(data);
    
    res=pd.merge(chiSquareData,lhs,on='CountryProv',how='inner')
    res=res.drop_duplicates(subset=['CountryProv'])
    
    #save res in chiSquare csv
    res.to_csv(join(self.dir_l3_arcgis, 'v2', 't11d-chisquared-ranks.csv'), index=False)

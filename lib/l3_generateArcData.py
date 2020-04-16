import pandas as pd
import numpy as np
historicalData=pd.read_csv('../../covid19-testing/l2-withConfirmed/t11c-confirmed+totalTests-historical.csv', delimiter=',')
chiSquareData=pd.read_csv('../../covid19-testing/l2-withConfirmed/t11d-chisquared-ranks.csv')
historicalData['CountryProv']=historicalData['CountryProv'].str.replace("[*]","")

countries= historicalData['CountryProv'].unique()
historicalData['Updated']="";



for country in countries:

    indexHist= np.where(historicalData.CountryProv==country)
    countryData=historicalData.iloc[indexHist]
    tests=countryData['total_cumul.all'];
    
    if sum(tests.notna())==0:
        continue
    indexfin=np.amax(np.where((tests.notna())))
    isNotUpdated=True

    if indexfin==len(tests) or indexfin==len(tests)-1:
        isNotUpdated=False

    if indexfin<len(tests):
        indexafter = range((indexfin+1),len(tests) )
        tests.iloc[indexafter]=tests.iloc[indexfin]
        countryData['total_cumul.all']=tests
    
    countryData['total_cumul.all']=countryData['total_cumul.all'].interpolate();
    if not(isNotUpdated):
        countryData['Updated']="*"
    else:
        countryData['Updated']=""

    historicalData.update(countryData)



historicalData['tests_per_mil']=np.floor(historicalData['total_cumul.all']*1000000/historicalData['Population'])
historicalData['ratio_confirmed_total_pct']=historicalData['ConfirmedCases']*100/historicalData['total_cumul.all']
historicalData['negative_cases']=historicalData['total_cumul.all']-historicalData['ConfirmedCases']

indexLatest=np.where(historicalData.Date==max(historicalData.Date))
selectColumns=historicalData[['CountryProv','Lat','Long','ConfirmedCases','Fatalities','total_cumul.all','negative_cases','tests_per_mil','ratio_confirmed_total_pct','Population','Updated']]

latest=selectColumns.iloc[indexLatest]

#save latest to csv
latest.to_csv('../../covid19-testing/ArcGIS/v2/t11c-confirmedtotalTests-latestOnly.csv')

dailyConfirmed=pd.Series([])
dailyNegative=pd.Series([])
for country in countries:
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


date=pd.concat([historicalData['Date'],historicalData['Date']], ignore_index=True)
historicalData['Negative']="Negative"
historicalData['Positive']="Positive"
positiveNegative=pd.concat([historicalData['Positive'],historicalData['Negative']], ignore_index=True)
daily=pd.concat([dailyConfirmed,dailyNegative], ignore_index=True)
cumulative=pd.concat([historicalData['ConfirmedCases'],historicalData['negative_cases']], ignore_index=True)
country=pd.concat([historicalData['CountryProv'],historicalData['CountryProv']], ignore_index=True)

data={'CountryProv':country,'Date':date,'dailyValue':daily,'cumulativeValue':cumulative, 'Positive/Negative':positiveNegative} 

stacked=pd.DataFrame(data);

#Save stacked in stacked csv
stacked.to_csv('../../covid19-testing/ArcGIS/v2/t11c-confirmedtotalTests-historical-stacked.csv')


data={'CountryProv':historicalData['CountryProv'],'Lat':historicalData['Lat'],'Long':historicalData['Long'],'Updated':historicalData['Updated']}
lhs=pd.DataFrame(data);

res=pd.merge(chiSquareData,lhs,on='CountryProv',how='inner')
res=res.drop_duplicates(subset=['CountryProv'])

#save res in chiSquare csv
res.to_csv('../../covid19-testing/ArcGIS/v2/t11d-chisquared-ranks.csv')
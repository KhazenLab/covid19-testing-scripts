library(zoo)
histData=read.csv("../covid19-testing/l2-withConfirmed/t11c-confirmed+totalTests-historical.csv")
histData$CountryProv=as.character(histData$CountryProv)
histData$Updated<-0
gsub('*',histData$CountryProv,'');
countries=unique(histData$CountryProv)

for(i in 1:length(countries))
{
  indexHist=which(histData$CountryProv==countries[i]);
  countryData=histData[indexHist,]
  tests=countryData$total_cumul.all;
  
  indexfin=max(which(!is.na(tests)))
  isNotUpdated<-T;
  if(indexfin==length(tests)||indexfin==(length(tests)-1))
  {
    isNotUpdated<-F;
  }
  
  if(is.finite(indexfin) && (indexfin<length(tests)))
  {
    
    indexafter=c((indexfin+1):length(tests))
    tests[indexafter]=tests[indexfin];
    countryData$total_cumul.all=tests;
    
  }
  
  
  
  tempdata<-zoo(countryData$total_cumul.all);
  tempdata_approx <- na.approx(tempdata)
  countryData$total_cumul.all[index(tempdata_approx)]=round(tempdata_approx,0)
  
  #indexNA=which(is.na(countryData$total_cumul.all))
  #countryData$total_cumul.all[indexNA]=countryData$ConfirmedCases;
  
  if(!isNotUpdated)
  {
    countryData$Updated="*"
  }
  else
  {
    countryData$Updated=""
  }
  histData[indexHist,]<-countryData
}

histData$tests_per_mil=histData$total_cumul.all*1000000/histData$Population;
histData$ratio_confirmed_total_pct=histData$ConfirmedCases*100/histData$total_cumul.all;
histData$negative_cases=histData$total_cumul.all-histData$ConfirmedCases;
histData$tests_per_mil=floor(histData$tests_per_mil)
write.csv(histData[,c(1:13)],"../covid19-testing/ArcGIS/v2/t11c-confirmedtotalTests-historical.csv",na="")
#End Historical


#Begin Latest
latest=histData[which(as.Date(histData$Date)==max(as.Date(histData$Date))),c("CountryProv","Lat","Long","ConfirmedCases","Fatalities","total_cumul.all","Population","tests_per_mil","ratio_confirmed_total_pct","negative_cases","Updated")]
names(latest)=c("CountryProv","Lat","Long","Max - ConfirmedCases","Max - Fatalities","Max - total_cumul.all","Max - Population","Max - tests_per_mil","Max - ratio_confirmed_total_pct","Max - negative_cases","Updated")
write.csv(latest,"../covid19-testing/ArcGIS/v2/t11c-confirmedtotalTests-latestOnly.csv",na="")
#End Latest

#Begin Daily Stacked
countries=unique(histData$CountryProv)
dates<-vector();
dailyConfirmed<-vector()
for(i in 1:length(countries))
{
  countryData=histData[which(histData$CountryProv==countries[i]),]
  dailyConfirmed<-append(dailyConfirmed,diff(c(0,countryData$ConfirmedCases)))
  
}


dailyTotal<-vector()
for(i in 1:length(countries))
{
  countryData=histData[which(histData$CountryProv==countries[i]),]
  
  
  total=c(0,countryData$total_cumul.all)
  
  
  dailyTotal<-append(dailyTotal,diff(total))
}



dailyNegative<-vector()
for(i in 1:length(countries))
{
  countryData=histData[which(histData$CountryProv==countries[i]),]
  
  negative=c(0,countryData$negative_cases)
  
  
  dailyNegative<-append(dailyNegative,diff(negative))
}


date= c(as.Date(histData$Date),as.Date(histData$Date))

negativeStr=rep("Negative",times=length(histData$ConfirmedCases))
positiveStr=rep("Positive",times=length(histData$ConfirmedCases))

positiveNegative=c(positiveStr,negativeStr)
daily=c(dailyConfirmed,dailyNegative)
cumulative=c(histData$ConfirmedCases,histData$negative_cases)

country=c(as.character(histData$CountryProv),as.character(histData$CountryProv))
lat=c(histData$Lat,histData$Lat)
long=c(histData$Long,histData$Long);

res= data.frame("CountryProv"=country,"Date"=date,"Lat"=lat,"Long"=long,"dailyValue"=daily,"cumulativeValue"=cumulative,"Positive.Negative"=positiveNegative)
names(res)=c("CountryProv","Date","Lat","Long","dailyValue","cumulativeValue","Positive/Negative")
write.csv(res,"../covid19-testing/ArcGIS/v2/t11c-confirmedtotalTests-historical-stacked.csv",na="")
#End Daily Stacked
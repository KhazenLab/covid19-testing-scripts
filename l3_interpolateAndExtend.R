library(zoo)
histData=read.csv("historical.csv")
histData$CountryProv=as.character(histData$CountryProv)
gsub('*',histData$CountryProv,'');
countries=unique(histData$CountryProv)
isUpdated<-vector();
for(i in 1:length(countries))
{
  indexHist=which(histData$CountryProv==countries[i]);
  countryData=histData[indexHist,]
  tests=countryData$total_cumul.all;
  
  indexfin=max(which(!is.na(tests)))
  isUpdated<-F;
  if(indexfin==length(tests))
  {
    isUpdated<-T;
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
  
  indexNA=which(is.na(countryData$total_cumul.all))
  countryData$total_cumul.all[indexNA]=countryData$ConfirmedCases;
  
  if(!isUpdated)
  {
    temp= countryData$CountryProv;
    temp=paste(temp,"*",sep="");
    countryData$CountryProv=as.character(temp);
    
  }
  histData[indexHist,]=countryData
}

histData$tests_per_mil=histData$total_cumul.all*1000000/histData$Population;
histData$ratio_confirmed_total_pct=histData$ConfirmedCases*100/histData$total_cumul.all;
histData$negative_cases=histData$total_cumul.all-histData$ConfirmedCases;
histData$tests_per_mil=floor(histData$tests_per_mil)

#End Historical


#Begin Latest
latest=histData[which(as.Date(histData$Date)==max(as.Date(histData$Date))),c("CountryProv","Lat","Long","ConfirmedCases","Fatalities","total_cumul.all","Population","tests_per_mil","ratio_confirmed_total_pct","negative_cases")]

#End Latest

#Begin Daily Stacked

dates<-vector();
dailyConfirmed<-vector()
for(i in 1:length(countries))
{
  countryData=histData[which(histData$CountryProv==countries[i]),]
  dailyConfirmed<-append(dailyConfirmed,diff(c(0,countryData$ConfirmedCases)))
  
}
histData$dailyConfirmed=dailyConfirmed

dailyTotal<-vector()
for(i in 1:length(countries))
{
  countryData=histData[which(histData$CountryProv==countries[i]),]
  
  indexfirst=min(which(!is.na(countryData$total_cumul.all)))
  if(!is.finite(indexfirst))
  {
    total=c(0,countryData$total_cumul.all)
    
  }
  else
  {
    total=c(countryData$total_cumul.all[c(1:indexfirst-1)],0,countryData$total_cumul.all[c(indexfirst:length(countryData$total_cumul.all))])
  }
  dailyTotal<-append(dailyTotal,diff(total))
}
histData$dailyTotal=dailyTotal


dailyNegative<-vector()
for(i in 1:length(countries))
{
  countryData=histData[which(histData$CountryProv==countries[i]),]
  
  indexfirst=min(which(!is.na(countryData$negative_cases)))
  if(!is.finite(indexfirst))
  {
    negative=c(0,countryData$negative_cases)
    
  }
  else
  {
    negative=c(countryData$negative_cases[c(1:indexfirst-1)],0,countryData$negative_cases[c(indexfirst:length(countryData$negative_cases))])
  }
  dailyNegative<-append(dailyNegative,diff(negative))
}
histData$dailyNegative=dailyNegative

date= c(histData$Dates,histData$dates)

negativeStr=rep("Negative",times=length(histData$ConfirmedCases))
positiveStr=rep("Positive",times=length(histData$ConfirmedCases))

positiveNegative=c(positiveStr,negativeStr);
daily=c(dailyConfirmed,dailyNegative);
cumulative=c(histData$ConfirmedCases,histData$negative_cases);

country=c(as.character(histData$CountryProv),as.character(histData$CountryProv))
lat=c(histData$Lat,histData$Lat);
long=c(histData$Long,histData$Long);

res= data.frame("CountryProv"=country,"Lat"=lat,"Long"=long,"dailyValue"=daily,"cumulativeValue"=cumulative,"Positive.Negative"=positiveNegative)


#End Daily Stacked
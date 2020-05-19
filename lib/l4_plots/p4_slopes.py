# -*- coding: utf-8 -*-
"""
From gdrive/biominers/halim/Rate-of-increase.ipynb
"""

from os.path import join
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.sandbox.stats.multicomp import multipletests
import matplotlib.pyplot as plt

from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row, column, widgetbox
from bokeh.plotting import figure, ColumnDataSource, output_file
from bokeh.models.widgets import Div
from bokeh.models import RangeSlider, Slider, Slope, Legend, LegendItem, CDSView, GroupFilter
from bokeh.transform import factor_cmap



def determineSlope(dataset,df_pop, nbDays, nbDaysEnd, rollingAvg):
  df_lastHist=dataset
  countries=  dataset["CountryProv"].unique()
  
  arr_country=[]
  arr_slopeCases=[]
  arr_slopePvalCases=[]
  arr_slopeTests=[]
  arr_slopePvalTests=[]
  arr_weeklyTestsPerc=[]
  arr_weeklyCasesPerc=[]
  countTests=0
  countSpikes=0
  for country in countries:
    df_countryData= df_lastHist[df_lastHist["CountryProv"]==country]
    dailyPositives= df_countryData["ConfirmedCases"]
    dailyTests= df_countryData["tests_cumulNoSpike"]
    dailyPositives= dailyPositives.diff().rolling(rollingAvg, min_periods=1).mean().tail(nbDays).dropna()
    dailyTests= dailyTests.diff().rolling(rollingAvg, min_periods=1).mean().tail(nbDays).dropna()
    
    if(len(dailyTests)<=1 | len(dailyPositives)<=1):
      continue
    if((dailyPositives.sum()==0) | (dailyTests.sum()==0) ):
      continue 
    
    if(len(dailyTests)>1):
      slopeTests, interceptTests, r_valueTests, p_valueTests, std_errTests = stats.linregress(dailyTests.index-dailyTests.index[0],dailyTests)

    else:
      slopeTests=np.nan
      p_valueTests=np.nan
    
    slopeCases, interceptCases, r_valueCases, p_valueCases, std_errCases = stats.linregress(dailyPositives.index-dailyPositives.index[0],dailyPositives)

    arr_weeklyCasesPerc.append(100*(dailyPositives.iloc[-1]-dailyPositives.iloc[0])/(dailyPositives.iloc[-1]))
    arr_weeklyTestsPerc.append(100*(dailyTests.iloc[-1]-dailyTests.iloc[0])/(dailyTests.iloc[-1]))
    arr_country.append(country)
    arr_slopeCases.append(slopeCases)
    arr_slopePvalCases.append(p_valueCases)
    arr_slopeTests.append(slopeTests)
    arr_slopePvalTests.append(p_valueTests)

  arr_slopePvalCases=multipletests(arr_slopePvalCases, method='bonferroni')[1]
  arr_slopePvalTests=multipletests(arr_slopePvalTests, method='bonferroni')[1]
  df_countryAvg=pd.DataFrame({"CountryProv":arr_country,"casesSlope":arr_slopeCases,"casesSlopePval":arr_slopePvalCases,"testsSlope":arr_slopeTests,"testsSlopePval":arr_slopePvalTests,'testsWeeklyPerc':arr_weeklyTestsPerc,'casesWeeklyPerc':arr_weeklyCasesPerc})
  return df_countryAvg

    
def editplotcolors(p1):
  p1.outline_line_width = 0
  p1.xaxis.axis_label_text_font_style=p1.yaxis.axis_label_text_font_style="normal"
  p1.border_fill_color = p1.background_fill_color = "#464646"
  p1.xaxis.axis_label_text_color = p1.yaxis.axis_label_text_color = 'whitesmoke'
  p1.xaxis.major_tick_line_color=p1.xaxis.minor_tick_line_color=p1.xaxis.axis_line_color="whitesmoke"
  p1.yaxis.major_tick_line_color=p1.yaxis.minor_tick_line_color=p1.yaxis.axis_line_color ="whitesmoke"
  p1.xaxis.major_label_text_color=p1.yaxis.major_label_text_color="whitesmoke"
  p1.ygrid.grid_line_alpha = 0.3
  p1.xgrid.grid_line_alpha = 0.3
  p1.xaxis.major_label_orientation=np.pi/4
  p1.title.text_color="whitesmoke"


def extend(tests_var):
  tests=tests_var.copy()
  # add 1 since R is 1-based and py is 0-based
  indexfin=np.amax(np.where((tests.notna()))) + 1
  isUpdated = (indexfin==len(tests)) or (indexfin==(len(tests)-1))
  # forward-fill the last NA for the sake of visualization
  tests.iloc[indexfin-1:] = tests.iloc[indexfin-1:].fillna(method="ffill")
  return(pd.Series(tests))


def read_csv(dir_gitrepo):
  df_hist= pd.read_csv(join(dir_gitrepo, "l2-withConfirmed", "interpolated_by_transformation.csv"))
  df_pop= pd.read_csv(join(dir_gitrepo, "l0-notion_tables","t11c-country_metadata.csv"))
  df_hist["Date"]=pd.to_datetime(df_hist["Date"])

  
  countries=df_hist["CountryProv"].unique()
  for country in countries:
    if df_hist.loc[df_hist["CountryProv"]==country,"tests_cumulNoSpike"].isnull().all():
      continue
    df_hist["tests_cumulNoSpike"].update(extend(df_hist.loc[df_hist["CountryProv"]==country,"tests_cumulNoSpike"]))
      
  return df_hist, df_pop


def figures_slopes(df_slopes,df_pop):
  nbStart=7
  nbEnd=0
  rolling=7
  df_countrySlopes=determineSlope(df_slopes,df_pop, nbStart, nbEnd, rolling)
  df_countrySlopes=df_countrySlopes.dropna()
  #df_countrySlopes=df_countrySlopes[df_countrySlopes.casesSlopePval<0.05]
  #df_countrySlopes=df_countrySlopes[df_countrySlopes.testsSlopePval<0.05]
  df_countrySlopes["temp"]="0"
  df_countrySlopes.loc[df_countrySlopes.testsWeeklyPerc>=df_countrySlopes.casesWeeklyPerc, ['temp']] = "1"
  df_countrySlopes=ColumnDataSource(data=df_countrySlopes.copy().dropna())
  gf = GroupFilter(column_name='temp', group="1")
  view1 = CDSView(source=df_countrySlopes, filters=[gf])
  gf = GroupFilter(column_name='temp', group="0")
  view2 = CDSView(source=df_countrySlopes, filters=[gf])
  
  
  TOOLTIPS = [
        ("Country/Region", "@CountryProv"),
        ("Cases Rate (%)","@casesWeeklyPerc"),
        ("Tests Rate (%)","@testsWeeklyPerc"),
  ]
  
                         
  p1=figure(tooltips=TOOLTIPS,tools=",pan,tap,box_zoom,reset",title="Generated on the basis of "+str(rolling)+" day moving average")
  r1=p1.scatter('casesWeeklyPerc','testsWeeklyPerc',source=df_countrySlopes, size=12,color='#73b2ff',legend_label='Tests Rate > Cases Rate',view=view1)
  r2=p1.scatter('casesWeeklyPerc','testsWeeklyPerc',source=df_countrySlopes, size=12,color='#ff7f7f',legend_label='Tests Rate < Cases Rate',view=view2)
  p1.xaxis.axis_label = 'Weekly Rate of Change for Positive Cases(%)'
  p1.yaxis.axis_label =  'Weekly Rate of Change for Nb. Tests(%)'

  
  
  p1.ray([0], [0], length=0, angle=np.pi,color = 'white')
  p1.ray([0], [0], length=0, angle=0,color = 'white')
  p1.ray([0], [0], length=0, angle=np.pi/2,color = 'white')
  p1.ray([0], [0], length=0, angle=3*np.pi/2,color = 'white')

  editplotcolors(p1)
  slope = Slope(gradient=1, y_intercept=0,
              line_color='white', line_dash='dashed', line_width=2)

  p1.add_layout(slope)
  
  p1.legend.background_fill_alpha=0.8
  p1.legend.background_fill_color="#262626"
  p1.legend.border_line_alpha=0
  p1.legend.label_text_color="whitesmoke"
  p1.legend.location = 'bottom_right'
  p1.toolbar_location="right"
  from bokeh.layouts import row, column, widgetbox
  return df_countrySlopes, p1

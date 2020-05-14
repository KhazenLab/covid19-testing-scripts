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
from bokeh.models import RangeSlider, Slider, Slope, Legend, LegendItem




def determineSlope(dataset,df_pop, nbDays, nbDaysEnd, rollingAvg):
  mask = (dataset['Date'] > max(dataset['Date'])- pd.DateOffset(nbDays+1)) & (dataset['Date'] <= max(dataset['Date'] - pd.DateOffset(nbDaysEnd)))
  countries=  dataset["CountryProv"].unique()
  df_lastHist=dataset[mask]
  arr_country=[]
  arr_slopeCases=[]
  arr_slopePvalCases=[]
  arr_slopeTests=[]
  arr_slopePvalTests=[]
  for country in countries:
    df_countryData= df_lastHist[df_lastHist["CountryProv"]==country]
    population= int(df_pop.loc[df_pop["CountryProv"]==country,"Population"])
    dailyPositives= df_countryData["ConfirmedCases"].diff().rolling(rollingAvg, min_periods=1).mean().dropna()
    dailyTests= df_countryData["tests_cumulNoSpike"].diff().rolling(rollingAvg, min_periods=1).mean().dropna()
    if(len(dailyTests)>1):
      slopeTests, interceptTests, r_valueTests, p_valueTests, std_errTests = stats.linregress(dailyTests.index-dailyTests.index[0],dailyTests/population) 

    else:
      slopeTests=np.nan
      p_valueTests=np.nan
    
    slopeCases, interceptCases, r_valueCases, p_valueCases, std_errCases = stats.linregress(dailyPositives.index-dailyPositives.index[0],dailyPositives/population)
   
    arr_country.append(country)
    arr_slopeCases.append(slopeCases)
    arr_slopePvalCases.append(p_valueCases)
    arr_slopeTests.append(slopeTests)
    arr_slopePvalTests.append(p_valueTests)

  arr_slopePvalCases=multipletests(arr_slopePvalCases, method='bonferroni')[1]
  arr_slopePvalTests=multipletests(arr_slopePvalTests, method='bonferroni')[1]
  df_countryAvg=pd.DataFrame({"CountryProv":arr_country,"casesSlope":arr_slopeCases,"casesSlopePval":arr_slopePvalCases,"testsSlope":arr_slopeTests,"testsSlopePval":arr_slopePvalTests})
  return df_countryAvg

    
def editplotcolors(p1):
  p1.outline_line_width = 0
  p1.xaxis.axis_label_text_font_style=p1.yaxis.axis_label_text_font_style="normal"
  p1.border_fill_color = p1.background_fill_color = "#464646"
  p1.xaxis.axis_label_text_color = p1.yaxis.axis_label_text_color = 'whitesmoke'
  p1.xaxis.major_tick_line_color=p1.xaxis.minor_tick_line_color=p1.xaxis.axis_line_color="whitesmoke"
  p1.yaxis.major_tick_line_color=p1.yaxis.minor_tick_line_color=p1.yaxis.axis_line_color ="whitesmoke"
  p1.xaxis.major_label_text_color=p1.yaxis.major_label_text_color="whitesmoke"
  p1.xgrid.visible = False
  p1.ygrid.visible = False
  p1.xaxis.major_label_orientation=np.pi/4


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
  nbStart=14
  nbEnd=0
  rolling=7
  df_countrySlopes=determineSlope(df_slopes,df_pop, nbStart, nbEnd, rolling)
  df_countrySlopes=df_countrySlopes.dropna()
  df_countrySlopes=df_countrySlopes[df_countrySlopes.casesSlopePval<0.05]
  df_countrySlopes=df_countrySlopes[df_countrySlopes.testsSlopePval<0.05]
  df_countrySlopes["color"]="#ff7f7f"
  df_countrySlopes.loc[df_countrySlopes.testsSlope>=df_countrySlopes.casesSlope, ['color']] = "#73b2ff"

  df_countrySlopes=ColumnDataSource(data=df_countrySlopes.copy().dropna())
  
  TOOLTIPS = [
      ("Cases Slope","@casesSlope"),
      ("Tests Slope","@testsSlope"),
      ("Country/Region", "@CountryProv"),
  ]
  
  title = Div(text="<h3>Generated from T-"+str(nbStart)+" to T-"+str(nbEnd)+" on the basis of "+str(rolling)+" day moving average</h3>",width=1000)
  
  p1=figure(plot_width=500,plot_height=500,tooltips=TOOLTIPS)
  r1=p1.scatter('casesSlope','testsSlope',source=df_countrySlopes, size=12,color='color')
  p1.xaxis.axis_label = 'Daily Cases Slope'
  p1.yaxis.axis_label =  'Daily Tests Slope'
  
  
  p1.ray([0], [0], length=0, angle=np.pi,color = 'white')
  p1.ray([0], [0], length=0, angle=0,color = 'white')
  p1.ray([0], [0], length=0, angle=np.pi/2,color = 'white')
  p1.ray([0], [0], length=0, angle=3*np.pi/2,color = 'white')

  editplotcolors(p1)
  slope = Slope(gradient=1, y_intercept=0,
              line_color='white', line_dash='dashed', line_width=2)

  p1.add_layout(slope)

  legend = Legend(items=[
    LegendItem(label="Tests Slope < Cases Slope", renderers=[r1], index=0),
    LegendItem(label="Tests Slope > Cases Slope", renderers=[r1], index=1),

  ])

  legend.background_fill_alpha=0
  legend.border_line_alpha=0
  legend.label_text_color="whitesmoke"
  p1.add_layout(legend, 'above')
  p1.toolbar_location="right"
  
  from bokeh.layouts import row, column, widgetbox
  return widgetbox(title), p1

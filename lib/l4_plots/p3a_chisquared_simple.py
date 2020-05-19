# -*- coding: utf-8 -*-
"""Notebook t11d
   Bokeh dashboard code same as postprocessed dashboard above
"""


from os.path import join
import pandas as pd
import numpy as np

from bokeh.layouts import gridplot, column
from bokeh.models import CDSView, ColumnDataSource, GroupFilter, CustomJS, LabelSet, Slope, Legend, LegendItem, HoverTool, BooleanFilter
from bokeh.plotting import figure, save, output_file



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
  p1.title.text_color="whitesmoke"
  


def figures_chisq_simple(init_group, df_chisq):
    
    source = ColumnDataSource(df_chisq)
    
    gf = GroupFilter(column_name='CountryProv', group=init_group)
    view1 = CDSView(source=source, filters=[gf])
    
    booleans = [True if float(case_detrended) >= 0 else False for case_detrended in source.data['case_detrended']]
    t1_view = CDSView(source=source, filters=[gf , BooleanFilter(booleans)])
    
    booleans = [True if float(case_detrended) < 0 else False for case_detrended in source.data['case_detrended']]
    t2_view = CDSView(source=source, filters=[gf , BooleanFilter(booleans)])
    
    p_b1_tooltip = [
      ("Date","@Date{%F}"),
      ("Thresholds Min","@threshold_min_eps"),
      ("Thresholds Max", "@threshold_max_eps"),
      ("Positive Cases", "@case_mvsum07"),
    ]
    
    p_b2_tooltip = [
      ("Date","@Date{%F}"),
      ("Detrended Cases", "@case_detrended"),
    ]
    p_formatters={
        '@Date'      : 'datetime'
    }
    plot_size_and_tools = {'tools':['box_select', 'reset', 'help', 'box_zoom'],
                           'x_axis_type': 'datetime'}
    
    # FIXME couldnt do p_a1.line below, so using hack of varea
    p_b1 = figure(title="Confirmed cases", **plot_size_and_tools)
    c_b1b = p_b1.varea(x='Date', y1='threshold_min_eps', y2='threshold_max_eps', source=source, color='grey', view=view1, legend_label="Range of 14-day expectation")
    c_b1a = p_b1.circle(x='Date', y='case_ma07', source=source, color='red', view=view1, legend_label="7-day average")

    p_b2 = figure(title="Detrended Cases (7-day Moving Average of cases minus their expected value)",**plot_size_and_tools)
    c_b2a = p_b2.scatter(x='Date', y='case_detrended', source=source,color='#73b2ff',legend_label="Above Threshold", view=t2_view)
    c_b2a = p_b2.scatter(x='Date', y='case_detrended', source=source,color='#ff7f7f',legend_label="Below Threshold", view=t1_view)
    editplotcolors(p_b1)
    editplotcolors(p_b2)
    p_b1.xaxis.axis_label = 'Date'
    p_b1.yaxis.axis_label =  'Positive Cases'
    p_b2.xaxis.axis_label = 'Date'
    p_b2.yaxis.axis_label =  'Detrended Number of Cases'
    
    p_b1.add_tools(HoverTool(tooltips=p_b1_tooltip,formatters=p_formatters))
    p_b2.add_tools(HoverTool(tooltips=p_b2_tooltip,formatters=p_formatters))
    
    p_b1.legend.location = 'top_left'
    p_b1.legend.background_fill_alpha=0.8
    p_b1.legend.background_fill_color="#262626"
    p_b1.legend.border_line_alpha=0
    p_b1.legend.label_text_color="whitesmoke"
   
   
    p_b2.legend.background_fill_alpha=0.8
    p_b2.legend.background_fill_color="#262626"
    p_b2.legend.border_line_alpha=0
    p_b2.legend.label_text_color="whitesmoke"
    p_b2.legend.location = 'bottom_left'
    
    return source, c_b1b, p_b1,p_b2



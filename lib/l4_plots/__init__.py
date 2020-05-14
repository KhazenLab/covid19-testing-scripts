# -*- coding: utf-8 -*-
"""t12b-shadi-stats per source again but using l2 data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16GiHxAP6SPxWYCugRVF-cV3EVxU2zdY6

Plotting counts per source
"""

from os.path import join
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib
import datetime as dt



class L4Plots:
  """
  Class that reads csv file from l2/historical and generates plots for l4_plots subdir
  """
  def __init__(self):
    self.dt_now = dt.datetime.now().strftime("%Y%m%d_%H%M%S")


  def read_csv(self, dir_gitrepo):
    csv_l2_historical = join(dir_gitrepo, "l2-withConfirmed", "t11c-confirmed+totalTests-historical.csv")
    df_agg = pd.read_csv(csv_l2_historical)
    df_agg.Date = pd.to_datetime(df_agg.Date)

    # Prep plot by using the selected source per triplet
    #This drops the duplicated datapoints (i.e. if a point comes from owid and we get it too, we shouldn't count our point)
    
    
    # for backward compatiability with l1 data
    df_agg["Location"] = df_agg["CountryProv"]
    
    df_agg3 = df_agg[["Location", "Date", "total_cumul.source"]].copy()
    df_agg3 = df_agg3.groupby(["Date", "total_cumul.source"]).count()
    df_agg3 = df_agg3.unstack("total_cumul.source")
    df_agg3.columns = df_agg3.columns.droplevel()
    
    ## show till date - 1. TODO drop this later
    #df_agg3.reset_index(inplace=True)
    #dt_max = df_agg3.Date.max() - pd.to_timedelta(1,'d')
    #df_agg3 = df_agg3[df_agg3.Date <= dt_max]
    #df_agg3.set_index("Date", inplace=True)
    
    # merge roser and ortiz
    df_agg3["owid/roser"] = df_agg3["owid/roser"].fillna(0) + df_agg3["owid/ortiz"].fillna(0)
    del df_agg3["owid/ortiz"]
    
    df_agg3 = df_agg3[["owid/roser", "covidtracking.com", "wiki", "worldometers", "biominers"]]
    
    df_agg3 = df_agg3.rename(columns={
        "owid/roser": "OWID",
        "covidtracking.com": "CTP",
        "wiki": "Wikipedia",
        "worldometers": "Worldometers",
        "biominers": "LAU manual subset"
    })

    self.df_agg3 = df_agg3


  def prep_plots(self):
    # http://stackoverflow.com/questions/3899980/ddg#3900167
    font = {'family' : 'DejaVu Sans',
            'weight' : 'normal',
            'size'   : 22}
    
    matplotlib.rc('font', **font)


  def plot_line(self, dir_plot_destination):
    # line plot
    df_agg3 = self.df_agg3

    plt.figure(figsize=(15,8))
    filled_markers = ('o', 'v', '^', '<', '>', 's', '8', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
    ax=sns.lineplot(data=df_agg3, markers=filled_markers)
    
    # 737530 is for 2020-04-15
    last_date = (df_agg3.index.max() - pd.to_datetime(dt.date(2020,4,15))).days
    extraticks = [737530+last_date]
    plt.xticks(list(plt.xticks()[0]) + extraticks)
    
    ax.set_ylabel("Number of daily country/state pairs")
    plt.xticks(rotation=45)
    plt.grid(alpha=.1)
    plt.ylim(0)
    plt.xlim(right=df_agg3.index.max())
    
    #fn_line = join(dir_plot_destination, 't12b-plotSourcesOverTime-lines-v%s.png'%self.dt_now)
    fn_line = join(dir_plot_destination, 't12b-plotSourcesOverTime-lines.png')
    #plt.savefig(fn_line, dpi = 300, bbox_inches="tight")
    plt.savefig(fn_line, dpi = 100, bbox_inches="tight")
    print(f"Saved to {fn_line} (at 100 dpi)")


  def plot_stacked(self, dir_plot_destination):
    # https://python-graph-gallery.com/251-stacked-area-chart-with-seaborn-style/
    # stacked area plot
    df_agg3 = self.df_agg3
    
    # Data
    x = df_agg3.index
    y=df_agg3.fillna(0).transpose().values
     
    # Plot
    plt.figure(figsize=(15,8))
    ax = plt.stackplot(x, y, labels=df_agg3.columns)
    plt.xlim(x.min(), x.max())
    plt.legend(loc='upper left')
    plt.ylabel("Countries/states with historical data")
    plt.xlabel("Date")
    
    # Add extra tick for May 3 since the automatic ticks stop at May 1
    #last_date = (df_agg3.index.max() - pd.to_datetime(dt.date(2020,4,15))).days
    ## 737530 represents 04-15
    #extraticks = [737530+last_date] # append last date
    ##extraticks = []
    #existingticks = list(plt.xticks()[0])
    ## drop 2020-05-01 because it's too close to 05-03
    #existingticks = existingticks[0:(len(existingticks)-1)]
    #plt.xticks(existingticks + extraticks)
    
    plt.xticks(rotation=45, ha="right")
    
    plt.grid(alpha=.2)
    
    # FIXME set an xlim on 2020-05-01 for lancet correspondence, but that got rejected
    #plt.xlim(right=dt.date(2020,5,1))
    
    # png for doc, and jpg for attachment to submission
    #fn_st_png = join(dir_plot_destination, 't12b-plotSourcesOverTime-stacked-v%s.png'%self.dt_now)
    fn_st_png = join(dir_plot_destination, 't12b-plotSourcesOverTime-stacked.png')
    #plt.savefig(fn_st_png, dpi = 300, bbox_inches="tight")
    plt.savefig(fn_st_png, dpi = 100, bbox_inches="tight")
    print(f"Saved to {fn_st_png} (at 100 dpi)")

    # disabled because it doesn't run on my laptop, but works fine on colab
    #fn_st_jpg = join(dir_plot_destination, 't12b-plotSourcesOverTime-stacked-v%s.jpg'%self.dt_now)
    #plt.savefig(fn_st_jpg, dpi = 300, bbox_inches="tight")

############################################################

from bokeh.layouts import gridplot
from bokeh.models import CDSView, ColumnDataSource, GroupFilter
from bokeh.models import CustomJS
from bokeh.plotting import figure, show
import pandas as pd
from bokeh.plotting import output_file
from bokeh.layouts import column
from bokeh.plotting import save


class PostprocessingDashboard:
  """Notebook t16a"""

  def read_csv(self, dir_gitrepo):
    dir_l2_withConf = join(dir_gitrepo, "l2-withConfirmed")
    df = pd.read_csv(join(dir_l2_withConf, "interpolated_by_transformation.csv"))
    df["Date"] = pd.to_datetime(df.Date)
    
    # replace nans: https://github.com/bokeh/bokeh/issues/4472#issuecomment-225676759
    for key in df:
        df[key] = ['NaN' if pd.isnull(value) else value for value in df[key]]

    self.df = df
        

  def to_html(self, dir_plot_destination):
    fn_dest = join(dir_plot_destination, "t16a-postprocessing_dashboard.html")
    output_file(fn_dest)
    
    source = ColumnDataSource(self.df)
    
    init_group = 'Lebanon'
    gf = GroupFilter(column_name='CountryProv', group=init_group)
    view1 = CDSView(source=source, filters=[gf])
    
    plot_size_and_tools = {'plot_height': 300, 'plot_width': 300,
                            'tools':['box_select', 'reset', 'help', 'box_zoom'],
                          'x_axis_type': 'datetime'}
    
    p_cc_ori = figure(title="Confirmed cases: original", **plot_size_and_tools)
    c_cc_ori = p_cc_ori.circle(x='Date', y='ConfirmedCases', source=source, color='black', view=view1)
    
    p_cc_cl = figure(title="Confirmed cases: eased spikes", **plot_size_and_tools)
    c_cc_cl = p_cc_cl.circle(x='Date', y='cases_cumulClean', source=source, color='red', view=view1)
 
    p_cto = figure(title="Cumulative Tests: original", **plot_size_and_tools)
    c_cto = p_cto.circle(x='Date', y='total_cumul.all', source=source, color='black', view=view1)
    
    p_ci = figure(title="Cumulative Tests: interpolated", **plot_size_and_tools)
    c_ci = p_ci.circle(x='Date', y='tests_cumulInterpolated', source=source, view=view1, color='red')
    
    p_cns = figure(title="Cumulative Tests: eased spikes", **plot_size_and_tools)
    c_cns = p_cns.circle(x='Date', y='tests_cumulNoSpike', source=source, view=view1, color='red')
    
    g = gridplot([[p_cc_ori, p_cc_cl], [p_cto, p_ci, p_cns]])
    
    # from https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html#select
    callback = CustomJS(args=dict(vf=c_cc_ori.view.filters[0], source=source), code="""
    console.log(vf.group);
    console.log(cb_obj.value);
        vf.group = cb_obj.value;
        source.change.emit();
    """)
    from bokeh.models import Select
    select = Select(title="Country/State:", value=init_group, options=list(self.df.CountryProv.unique()))
    select.js_on_change('value', callback)
    
    layout = column(select, g)
    save(layout)
    print(f"Saved to {fn_dest}")

######################################

class SlopesChisquaredDashboardDetailed:
  """
  Combines p3 slopes scatter plot with p4 chi-squared threshold plots
  """

  def read_csv(self, dir_gitrepo):
    from .p3_chisquared import read_csv as read_csv_chisq
    self.df_chisq = read_csv_chisq(dir_gitrepo)


  def to_html(self, dir_plot_destination):
    from .p3_chisquared import figures_chisq_detailed
    init_group = 'Lebanon'
    source_chisq, c_a1a, grid_chisq = figures_chisq_detailed(init_group, self.df_chisq)

    fn_dest = join(dir_plot_destination, "t11d-chisquared_dashboard-detailed.html")
    output_file(fn_dest)

    # link dropdown to filter data
    # from https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html#select
    callback = CustomJS(
      args=dict( vf=c_a1a.view.filters[0],
                 source_chisq=source_chisq
               ),
      code="""
        console.log(vf.group);
        console.log(cb_obj.value);
        vf.group = cb_obj.value;
        source_chisq.change.emit();
        """
      )
    from bokeh.models import Select
    select = Select(title="Country/State:", value=init_group, options=list(self.df_chisq.CountryProv.unique()))
    select.js_on_change('value', callback)
    
    # create layout of everything
    layout = column(select, grid_chisq)
    save(layout)
    print(f"Saved to {fn_dest}")


##################################

class SlopesChisquaredDashboardSimple:
  """
  Combines p3 slopes scatter plot with p4 chi-squared threshold plots
  """

  def read_csv(self, dir_gitrepo):
    from .p3_chisquared import read_csv as read_csv_chisq
    self.df_chisq = read_csv_chisq(dir_gitrepo)

    from .p4_slopes import read_csv as read_csv_slopes
    self.df_slopes, self.df_pop = read_csv_slopes(dir_gitrepo)


  def to_html(self, dir_plot_destination):
    from .p3_chisquared import figures_chisq_simple
    init_group = 'Lebanon'
    source_chisq, c_b1b, grid_chisq = figures_chisq_simple(init_group, self.df_chisq)

    from .p4_slopes import figures_slopes
    title_slopes, fig_slopes = figures_slopes(self.df_slopes,self.df_pop)

    fn_dest = join(dir_plot_destination, "t11d-chisquared_dashboard-simple.html")
    output_file(fn_dest)

    # link dropdown to filter data
    # from https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html#select
    callback = CustomJS(
      args=dict( vf=c_b1b.view.filters[0],
                 source_chisq=source_chisq
               ),
      code="""
        console.log(vf.group);
        console.log(cb_obj.value);
        vf.group = cb_obj.value;
        source_chisq.change.emit();
        """
      )
    from bokeh.models import Select
    select = Select(title="Country/State:", value=init_group, options=list(self.df_chisq.CountryProv.unique()))
    select.js_on_change('value', callback)
    
    # create layout of everything
    layout = column(title_slopes, fig_slopes, select, grid_chisq)
    save(layout)
    print(f"Saved to {fn_dest}")




# -*- coding: utf-8 -*-
"""Notebook t11d
   Bokeh dashboard code same as postprocessed dashboard above
"""


from os.path import join
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.sandbox.stats.multicomp import multipletests
import matplotlib.pyplot as plt


from bokeh.layouts import gridplot
from bokeh.models import CDSView, ColumnDataSource, GroupFilter
from bokeh.models import CustomJS
from bokeh.plotting import figure, show
import pandas as pd
from bokeh.plotting import output_file
from bokeh.layouts import column
from bokeh.plotting import save



def read_csv(dir_gitrepo):
    import click
    click.secho("As of 2020-05-13, remember that the l4/chi-squared dashboard requires running notebook t11d and downloading the resultant csv", fg="yellow")
    dir_l4 = join(dir_gitrepo, "l4-analysis")
    df = pd.read_csv(join(dir_l4, "t11d-chisquared-history-v20200512.csv"))
    df.rename(columns={"case_d2": "case_mvsum07", "control_d2": "control_mvsum07"}, inplace=True)
    df["Date"] = pd.to_datetime(df.Date)
    df["case_ma07"] = df["case_mvsum07"]/7
    df["control_ma07"] = df["control_mvsum07"]/7
    df["tests_ma07"] = df.case_ma07 + df.control_ma07
    df["threshold_min"] = df.threshold_min.round()
    df["threshold_max"] = df.threshold_max.round()
    df["case_ma07_eps"] = df.case_ma07*1.03
    df["tests_ma07_eps"] = df.tests_ma07*1.03
    df["threshold_min_eps"] = df.threshold_min*1.03
    df["threshold_max_eps"] = df.threshold_max*1.03
    df["ratio_daily"] = df.daily_conf / df.daily_tests * 100
    df["ratio_ma07"] = df.case_ma07 / df.tests_ma07 * 100
    df["case_detrended"] = df.case_mvsum07 - (df.threshold_min+df.threshold_max)/2

    # columns subset
    df = df[["CountryProv","Date",
             "daily_conf", "case_ma07", "case_mvsum07", "case_ma07_eps",
             "daily_tests", "tests_ma07", "tests_ma07_eps",
             #"control_mvsum07",
             "threshold_min", "threshold_max",
             "threshold_min_eps", "threshold_max_eps",
             "ratio_daily", "ratio_ma07",
             "case_detrended"
             ]]

    # replace nans: https://github.com/bokeh/bokeh/issues/4472#issuecomment-225676759
    #df = df.fillna("NaN")
    #for key in df:
    #    print(f"Replace {key} nans")
    #    df[key] = ['NaN' if pd.isnull(value) else value for value in df[key]]

    return df


def figures_chisq(init_group, df_chisq):
    source = ColumnDataSource(df_chisq)
    
    gf = GroupFilter(column_name='CountryProv', group=init_group)
    view1 = CDSView(source=source, filters=[gf])
    
    plot_size_and_tools = {'plot_height': 300, 'plot_width': 600,
                           'tools':['box_select', 'reset', 'help', 'box_zoom'],
                           'x_axis_type': 'datetime'
                          }
    
    # FIXME couldnt do p_a1.line below, so using hack of varea
    p_a1 = figure(title="Confirmed cases (daily vs 7-day moving avg)", **plot_size_and_tools)
    c_a1a = p_a1.circle(x='Date', y='daily_conf', source=source, color='black', view=view1)
    c_a1b = p_a1.varea(x='Date', y1='case_ma07', y2='case_ma07_eps', source=source, color='red', view=view1)
   
    p_a2 = figure(title="Total tests (daily vs 7-day moving avg)", **plot_size_and_tools)
    c_a2a = p_a2.circle(x='Date', y='daily_tests', source=source, color='black', view=view1)
    c_a2b = p_a2.varea(x='Date', y1='tests_ma07', y2="tests_ma07_eps", source=source, color='red', view=view1)

    p_b1 = figure(title="Confirmed and thresholds (7 vs 14-day sum, below threshold: good, above: bad, within: ok)", **plot_size_and_tools)
    c_b1b = p_b1.varea(x='Date', y1='threshold_min_eps', y2='threshold_max_eps', source=source, color='grey', view=view1)
    c_b1a = p_b1.circle(x='Date', y='case_mvsum07', source=source, color='red', view=view1)

    p_b2 = figure(title="Detrended cases (7-day ma, cases minus thresholds, negative: good, positive: bad)", **plot_size_and_tools)
    c_b2a = p_b2.circle(x='Date', y='case_detrended', source=source, color='green', view=view1)

    p_c1 = figure(title="Ratio case/total (daily)", **plot_size_and_tools)
    c_c1a = p_c1.circle(x='Date', y='ratio_daily', source=source, color='blue', view=view1)

    p_c2 = figure(title="Ratio case/total (7-day ma)", **plot_size_and_tools)
    c_c2a = p_c2.circle(x='Date', y='ratio_ma07', source=source, color='blue', view=view1)

    g = gridplot([[p_a1, p_a2], [p_b1, p_b2], [p_c1, p_c2]])

    return source, c_a1a, g



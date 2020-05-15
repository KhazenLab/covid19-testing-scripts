# -*- coding: utf-8 -*-
"""Notebook t11d
   Bokeh dashboard code same as postprocessed dashboard above
"""


from os.path import join
import pandas as pd
import numpy as np

from bokeh.layouts import gridplot, column
from bokeh.models import CDSView, ColumnDataSource, GroupFilter, CustomJS, LabelSet, Slope, Legend, LegendItem, HoverTool
from bokeh.plotting import figure, save, output_file
from bokeh.transform import factor_cmap



def read_csv(dir_gitrepo):
    import click
    click.secho("As of 2020-05-13, remember that the l4/chi-squared dashboard requires running notebook t11d and downloading the resultant csv", fg="yellow")
    dir_l4 = join(dir_gitrepo, "l4-analysis")
    df = pd.read_csv(join(dir_l4, "t11d-chisquared-history-v20200512.csv"))
    df.rename(columns={"case_d2": "case_mvsum07", "control_d2": "control_mvsum07"}, inplace=True)
    df["Date"] = pd.to_datetime(df.Date)
    return df


def postprocess(df, dir_gitrepo):
    df = df.copy()
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

    # FIXME is this redundant with diff2_07_excess field?
    df["case_det_diff07"] = df.case_detrended.diff(periods=7)

    # columns subset
    df = df[["CountryProv","Date",
             "daily_conf", "case_ma07", "case_mvsum07", "case_ma07_eps",
             "daily_tests", "tests_ma07", "tests_ma07_eps",
             #"control_mvsum07",
             "threshold_min", "threshold_max",
             "threshold_min_eps", "threshold_max_eps",
             "ratio_daily", "ratio_ma07",
             "case_detrended", "case_det_diff07"
             ]]

    # split out country name
    df["Country"] = df.CountryProv.str.split(" – ").apply(lambda x: x[0])

    # get US state iso code
    us_info = pd.read_csv(join(dir_gitrepo, "l1a-non-biominer_data", "covidtracking.com-info.csv"))
    us_info["name"] = "US – " + us_info["name"]
    df = df.merge(us_info[["state","name"]].rename(columns={"state":"us_code", "name":"CountryProv"}), how="left")

    # get international country code
    int_info = pd.read_csv(join(dir_gitrepo, "l1a-non-biominer_data", "github-lukes-countrycodes.csv"))
    country_renames = {
      "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
      "Iran \(Islamic Republic of\)": "Iran",
      "Bolivia \(Plurinational State of\)": "Bolivia",
      "Brunei Darussalam": "Brunei",
      "Congo, Democratic Republic of the": "Congo (Kinshasa)",
      "Côte d'Ivoire": "Cote d'Ivoire",
      "Lao People's Democratic Republic": "Laos",
      "Moldova, Republic of": "Moldova",
      "Russian Federation": "Russia",
      "Korea \(Democratic People's Republic of\)": "South Korea",
      "Taiwan, Province of China": "Taiwan",
      "Tanzania, United Republic of": "Tanzania",
      "Venezuela \(Bolivarian Republic of\)": "Venezuela",
      "Viet Nam": "Vietnam",
      "Palestine, State of": "West Bank and Gaza",
      "Myanmar": "Burma",
    }
    for k,v in country_renames.items():
      int_info["name"] = int_info["name"].str.replace(k, v)

    # manualy add kosovo
    int_info = int_info[["name","alpha-2", "region"]]
    int_info = pd.concat([int_info, pd.DataFrame([{"name": "Kosovo", "alpha-2": "KV", "region": "Europe"}])], axis=0)
    df = df.merge(int_info[["name","alpha-2", "region"]].rename(columns={"alpha-2":"int_code", "name":"Country"}), how="left")

    # merge us and international codes
    df["cp_code"] = df.us_code.fillna(df.int_code).fillna(df.CountryProv)
    df["region"] = df.region.fillna(df.CountryProv)
    # df.set_index("CountryProv").loc["US – Alabama"].head()

    df["Continent"] = df.CountryProv.apply(lambda g: "US" if g.startswith("US") else np.nan).fillna(df.region)

    # prep for agg
    df_ffill = df.groupby("CountryProv").apply(lambda g: g.fillna(method="ffill"))

    # add aggregated data for globe
    df_world = df_ffill.groupby("Date").sum().reset_index()
    df_world["CountryProv"] = "0 - World"
    df_world["Country"] = "0 - World"
    df_world["region"] = "Aggregates"
    df_world["cp_code"] = "World"
    df_world["Continent"] = "Aggregates"

    # add aggregated data per region
    df_reg = df_ffill.sort_values(["Continent", "Date"]).groupby(["Continent","Date"]).sum().reset_index() # apply(sum(g)) is slow. apply(g.sum()) requires reset_index(drop=True)
    df_reg["CountryProv"] = "0 - " + df_reg["Continent"]
    df_reg["Country"] = "0 - " + df_reg["Continent"]
    df_reg["region"] = "Aggregates"
    df_reg["cp_code"] = df_reg["Continent"]
    df_reg["Continent"] = "Aggregates"

    df = pd.concat([df, df_world], axis=0)
    df = pd.concat([df, df_reg], axis=0)

    # replace nans: https://github.com/bokeh/bokeh/issues/4472#issuecomment-225676759
    #df = df.fillna("NaN")
    #for key in df:
    #    print(f"Replace {key} nans")
    #    df[key] = ['NaN' if pd.isnull(value) else value for value in df[key]]

    return df


  
def figures_chisq_detailed(init_group, df_chisq):
    df_latest = df_chisq.groupby("CountryProv").apply(lambda g: g.tail(1)).reset_index(drop=True)
    df_latest["color"] = "#73b2ff"

    source_hist = ColumnDataSource(df_chisq)
    source_latest = ColumnDataSource(df_latest)

    # since cannot use View iwth LabelSet, creating a different source per continent
    srcLatest_continent = df_latest.groupby("Continent").apply(lambda g: ColumnDataSource(g))
    srcLatest_continent = srcLatest_continent.reset_index().rename(columns={0:"src"})
  
    gf = GroupFilter(column_name='CountryProv', group=init_group)
    view1 = CDSView(source=source_hist, filters=[gf])
    
    plot_size_and_tools = {'plot_height': 300, 'plot_width': 600,
                           'tools':['box_select', 'reset', 'help', 'box_zoom'],
                           'x_axis_type': 'datetime'
                          }
    
    # FIXME couldnt do p_a1.line below, so using hack of varea
    p_a1 = figure(title="Confirmed cases (daily vs 7-day moving avg)", **plot_size_and_tools)
    c_a1a = p_a1.circle(x='Date', y='daily_conf', source=source_hist, color='black', view=view1)
    c_a1b = p_a1.varea(x='Date', y1='case_ma07', y2='case_ma07_eps', source=source_hist, color='red', view=view1)
   
    p_a2 = figure(title="Total tests (daily vs 7-day moving avg)", **plot_size_and_tools)
    c_a2a = p_a2.circle(x='Date', y='daily_tests', source=source_hist, color='black', view=view1)
    c_a2b = p_a2.varea(x='Date', y1='tests_ma07', y2="tests_ma07_eps", source=source_hist, color='red', view=view1)

    p_b1 = figure(title="Confirmed and thresholds (7-day sum cases vs 14-day thresholds. Below threshold: good, above: bad, within: ok)", **plot_size_and_tools)
    c_b1b = p_b1.varea(x='Date', y1='threshold_min_eps', y2='threshold_max_eps', source=source_hist, color='grey', view=view1)
    c_b1a = p_b1.circle(x='Date', y='case_mvsum07', source=source_hist, color='red', view=view1)

    p_b2 = figure(title="Detrended cases (7-day-sum cases minus thresholds, negative: good, positive: bad)", **plot_size_and_tools)
    c_b2a = p_b2.circle(x='Date', y='case_detrended', source=source_hist, color='green', view=view1)

    p_c1 = figure(title="Ratio case/total (daily)", **plot_size_and_tools)
    c_c1a = p_c1.circle(x='Date', y='ratio_daily', source=source_hist, color='blue', view=view1)

    p_c2 = figure(title="Ratio case/total (7-day ma)", **plot_size_and_tools)
    c_c2a = p_c2.circle(x='Date', y='ratio_ma07', source=source_hist, color='blue', view=view1)

    # general-use lines
    slope_y0 = Slope(gradient=0, y_intercept=0, line_color='orange', line_width=50)
    slope_x0 = Slope(gradient=np.Inf, y_intercept=0, line_color='orange', line_width=50)

    # scatter plot
    view_us = CDSView(source=source_latest, filters=[GroupFilter(column_name='Continent', group="US")])
    view_other = CDSView(source=source_latest, filters=[GroupFilter(column_name='Continent', group="Other")])

    TOOLTIPS = [
        ("Country/Region", "@CountryProv"),
    ]
    p_cont = []
    for srcCont_i in srcLatest_continent.iterrows():
      srcCont_i = srcCont_i[1]
      p_d1=figure(plot_width=600,plot_height=400,tooltips=TOOLTIPS,title=srcCont_i.Continent)
      p_d1.scatter('case_detrended','case_det_diff07',source=srcCont_i.src, size=12,color='color') # , view=view_us
      p_d1.xaxis.axis_label = 'Cases detrended: values'
      p_d1.yaxis.axis_label =  'Cases detrended: diff07'
      from bokeh.models import LabelSet
      labels = LabelSet(x='case_detrended', y='case_det_diff07', text='cp_code', level='glyph',
               x_offset=5, y_offset=5, source=srcCont_i.src, render_mode='canvas')
      p_d1.add_layout(labels)
      p_d1.add_layout(slope_y0)
      p_d1.add_layout(slope_x0)
      p_cont.append(p_d1)

    # group plots into 3 per row
    # https://stackoverflow.com/a/1625013/4126114
    from itertools import zip_longest
    p_cont = list(zip_longest(*(iter(p_cont),) * 3))
    p_cont = [[e for e in t if e != None] for t in p_cont]

    g = gridplot([[p_a1, p_a2], [p_b1, p_b2], [p_c1, p_c2]] + p_cont)

    return source_hist, c_a1a, g


def figures_chisq_simple(init_group, df_chisq):
    
    df_chisq["color"]="#ff7f7f"
    df_chisq.loc[df_chisq.case_detrended>=0, ['color']] = "#73b2ff"
    source = ColumnDataSource(df_chisq)
    
    gf = GroupFilter(column_name='CountryProv', group=init_group)
    view1 = CDSView(source=source, filters=[gf])
    
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
    plot_size_and_tools = {
                           'tools':['box_select', 'reset', 'help', 'box_zoom'],
                           'x_axis_type': 'datetime'
                           }
    
    # FIXME couldnt do p_a1.line below, so using hack of varea
    p_b1 = figure(title="Confirmed and Thresholds (7 vs 14-day Sum)", **plot_size_and_tools)
    c_b1b = p_b1.varea(x='Date', y1='threshold_min_eps', y2='threshold_max_eps', source=source, color='grey', view=view1)
    c_b1a = p_b1.circle(x='Date', y='case_mvsum07', source=source, color='red', view=view1)

    p_b2 = figure(title="Detrended Cases (7-day Moving Average, Cases Minus Thresholds)",**plot_size_and_tools)
    c_b2a = p_b2.scatter(x='Date', y='case_detrended', source=source, color='color', view=view1)
    editplotcolors(p_b1)
    editplotcolors(p_b2)
    p_b1.xaxis.axis_label = 'Date'
    p_b1.yaxis.axis_label =  'Positive Cases'
    p_b2.xaxis.axis_label = 'Date'
    p_b2.yaxis.axis_label =  'Detrended Number of Cases'
    
    p_b1.add_tools(HoverTool(tooltips=p_b1_tooltip,formatters=p_formatters))
    p_b2.add_tools(HoverTool(tooltips=p_b2_tooltip,formatters=p_formatters))
    
    legend = Legend(items=[
    LegendItem(label="asd", renderers=[c_b1b]),
    LegendItem(label="asdd", renderers=[c_b1a]),
    ])
    legend.background_fill_alpha=0.8
    legend.background_fill_color="#262626"
    legend.border_line_alpha=0
    legend.label_text_color="whitesmoke"
    p_b1.add_layout(legend)
    p_b1.legend.location = 'top_left'
    
    legend = Legend(items=[
    LegendItem(label="Detrended < 0 ", renderers=[c_b2a],index=0),
    LegendItem(label="Detrended > 0", renderers=[c_b2a],index=1),
    ])
    legend.background_fill_alpha=0.8
    legend.background_fill_color="#262626"
    legend.border_line_alpha=0
    legend.label_text_color="whitesmoke"
    p_b2.add_layout(legend)
    p_b2.legend.location = 'bottom_left'
    
    return source, c_b1b, p_b1,p_b2



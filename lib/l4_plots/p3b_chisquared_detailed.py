# -*- coding: utf-8 -*-
"""Notebook t11d
   Bokeh dashboard code same as postprocessed dashboard above
"""


from os.path import join
import pandas as pd
import numpy as np

from bokeh.layouts import gridplot, column
from bokeh.models import CDSView, ColumnDataSource, GroupFilter, CustomJS, LabelSet, Slope, Legend, LegendItem, HoverTool, Band
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
    df["threshold_min"] = df.threshold_min/7
    df["threshold_max"] = df.threshold_max/7


    df["case_ma07_eps"] = df.case_ma07*1.03
    #df["case_mvsum07_eps"] = df.case_mvsum07*1.03

    df["tests_ma07_eps"] = df.tests_ma07*1.03
    df["threshold_min_eps"] = df.threshold_min*0.99
    df["threshold_max_eps"] = df.threshold_max*1.01
    df["ratio_daily"] = df.daily_conf / df.daily_tests * 100
    df["ratio_ma07"] = df.case_ma07 / df.tests_ma07 * 100

    df["thres_mid"] = (df.threshold_min + df.threshold_max)/2
    df["case_detrended"] = df.case_ma07 - df.thres_mid
    df["caseDet_eps"] = df.case_detrended*1.05

    df["case_mvsd07"] = df.groupby("CountryProv").daily_conf.apply(lambda g: g.rolling(window=7).std())
    df["tests_mvsd07"] = df.groupby("CountryProv").daily_tests.apply(lambda g: g.rolling(window=7).std())

    #df["case_ma14"] = df.groupby("CountryProv").daily_conf.apply(lambda g: g.rolling(window=14).mean())
    #df["tests_ma14"] = df.groupby("CountryProv").daily_tests.apply(lambda g: g.rolling(window=14).mean())
    #df["case_ma14_eps"] = df.case_ma14*1.03
    #df["tests_ma14_eps"] = df.tests_ma14*1.03

    df['case_ma07_lower'] = df.case_ma07 - df.case_mvsd07
    df['case_ma07_upper'] = df.case_ma07 + df.case_mvsd07
    df['tests_ma07_lower'] = df.tests_ma07 - df.tests_mvsd07
    df['tests_ma07_upper'] = df.tests_ma07 + df.tests_mvsd07

    #df['case_mvsum07_lower'] = df.case_mvsum07 - df.case_mvsd07*7
    #df['case_mvsum07_upper'] = df.case_mvsum07 + df.case_mvsd07*7
    #df['tests_mvsum07_lower'] = df.control_mvsum07 + df.case_mvsum07 - df.tests_mvsd07*7
    #df['tests_mvsum07_upper'] = df.control_mvsum07 + df.case_mvsum07 + df.tests_mvsd07*7

    df["thresMinMinusMid"] = df.threshold_min - df.thres_mid
    df["thresMaxMinusMid"] = df.threshold_max - df.thres_mid
    df["caseMa07Lower_minusMid"] = df.case_ma07_lower - df.thres_mid
    df["caseMa07Upper_minusMid"] = df.case_ma07_upper - df.thres_mid

    # df.tail()[["CountryProv", "Date", "case_ma07", "case_mvsd07", "case_ma07_lower", "case_ma07_upper"]]

    # FIXME is this redundant with diff2_07_excess field?
    df["case_det_diff07"] = df.case_detrended.diff(periods=7)

    # columns subset
    #df = df[["CountryProv","Date",
    #         "daily_conf", "case_ma07", "case_mvsum07", "case_ma07_eps",
    #         "daily_tests", "tests_ma07", "tests_ma07_eps",
    #         #"control_mvsum07",
    #         "threshold_min", "threshold_max",
    #         "threshold_min_eps", "threshold_max_eps",
    #         "ratio_daily", "ratio_ma07",
    #         "case_detrended", "case_det_diff07"
    #         ]]

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
    df_world["Continent"] = "Agg/World" # used in p5 for each plot

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
    df_chisq["dt_str"] = df_chisq.Date.dt.strftime("%Y-%m-%d")
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
                           'x_axis_type': 'datetime',
                           'tooltips': [
                                ("Date", "@dt_str"),
                            ],
                          }

    
    # FIXME couldnt do p_a1.line below, so using hack of varea
    p_a1 = figure(title="Confirmed and thresholds. Below threshold: good, above: bad, within: ok", **plot_size_and_tools)
    p_a1.varea(x='Date', y1='case_ma07_lower', y2='case_ma07_upper', source=source_hist, color='pink', view=view1, fill_alpha=.7, legend_label="mean +/- std band")
    p_a1.varea(x='Date', y1='case_ma07', y2='case_ma07_eps', source=source_hist, color='red', view=view1, legend_label="7-day moving avg")
    #p_a1.varea(x='Date', y1='case_ma14', y2='case_ma14_eps', source=source_hist, color='purple', view=view1, legend_label="14-day moving avg")
    p_a1.varea(x='Date', y1='threshold_min_eps', y2='threshold_max_eps', source=source_hist, color='green', view=view1, fill_alpha=.7, legend_label="chi-squared thresholds band")

    # band: view= is not supported, so just using varea above
    #band = Band(base='Date', lower='case_ma07_lower', upper='case_ma07_upper', source=source_hist, level='underlay',
    #            fill_alpha=1.0, line_width=1, line_color='black', view=view1)
    #p_a1.add_layout(band)
    c_a1a = p_a1.circle(x='Date', y='daily_conf', source=source_hist, color='black', view=view1)

    # https://stackoverflow.com/a/51540955/4126114
    # https://docs.bokeh.org/en/latest/docs/user_guide/styling.html#inside-the-plot-area
    p_a1.legend.label_text_font_size = '6pt'
    p_a1.legend.location = "top_left"

   
    p_a2 = figure(title="Total tests (daily vs 7-day moving avg)", **plot_size_and_tools)
    p_a2.varea(x='Date', y1='tests_ma07_lower', y2='tests_ma07_upper', source=source_hist, color='pink', view=view1)
    p_a2.varea(x='Date', y1='tests_ma07', y2="tests_ma07_eps", source=source_hist, color='red', view=view1)
    #p_a2.varea(x='Date', y1='tests_ma14', y2="tests_ma14_eps", source=source_hist, color='purple', view=view1)
    p_a2.circle(x='Date', y='daily_tests', source=source_hist, color='black', view=view1)
    p_a2.x_range = p_a1.x_range # lock in the x axis so that zoom works simultaneously on all

    #p_b1 = figure(title="canceled: Confirmed and thresholds (7-day sum cases vs 14-day thresholds. Below threshold: good, above: bad, within: ok)", **plot_size_and_tools)
    #p_b1.varea(x='Date', y1='case_mvsum07_lower', y2='case_mvsum07_upper', source=source_hist, color='pink', view=view1)
    #p_b1.varea(x='Date', y1='case_mvsum07', y2='case_mvsum07_eps', source=source_hist, color='red', view=view1)
    #p_b1.varea(x='Date', y1='threshold_min_eps', y2='threshold_max_eps', source=source_hist, color='grey', view=view1)
    #p_b1.circle(x='Date', y='case_mvsum07', source=source_hist, color='red', view=view1, size=1)

    p_b2 = figure(title="Detrended cases. Negative: good, positive: bad", **plot_size_and_tools)
    p_b2.varea(x='Date', y1='thresMinMinusMid', y2='thresMaxMinusMid', source=source_hist, color='green', view=view1, legend_label="thresholds band", fill_alpha=0.7)
    p_b2.varea(x='Date', y1='caseMa07Lower_minusMid', y2='caseMa07Upper_minusMid', source=source_hist, color='pink', view=view1, legend_label="cases ma7 - threshold mid +/- std", fill_alpha=0.7)
    p_b2.varea(x='Date', y1='case_detrended', y2='caseDet_eps', source=source_hist, color='red', view=view1, legend_label="cases detrended")
    p_b2.circle(x='Date', y='case_detrended', source=source_hist, color='red', view=view1)
    p_b2.x_range = p_a1.x_range
    p_b2.legend.label_text_font_size = '6pt'
    p_b2.legend.location = "top_left"

    p_c1 = figure(title="Ratio case/total (daily)", **plot_size_and_tools)
    c_c1a = p_c1.circle(x='Date', y='ratio_daily', source=source_hist, color='blue', view=view1)

    p_c2 = figure(title="Ratio case/total (7-day ma)", **plot_size_and_tools)
    p_c2.circle(x='Date', y='ratio_ma07', source=source_hist, color='blue', view=view1)

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

    # p_b1, 
    g = gridplot([[p_a1, p_a2], [p_b2], [p_c1, p_c2]] + p_cont)

    return source_hist, c_a1a, g



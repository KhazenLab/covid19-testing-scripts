from bokeh.models import CDSView, ColumnDataSource, GroupFilter, TapTool, CustomJS, Slope
import pandas as pd
from bokeh.plotting import figure, show, output_file, save
from bokeh.layouts import gridplot, column, row
import numpy as np
from os.path import join


def figure_scatter_values(df_chisq):
    df_chisq["casema07_diff07"] = df_chisq.case_ma07.diff(periods=1)
    df_chisq["testsma07_diff07"] = df_chisq.tests_ma07.diff(periods=1)
    df_chisq["casedet_diff07"] = df_chisq.case_detrended.diff(periods=1)
    df_chisq["casedetpct_diff07"] = df_chisq.caseDet_pct.diff(periods=1)
    df_chisq["angle"] = df_chisq.testsma07_diff07 / df_chisq.casema07_diff07 * 3.14
    df_chisq["casema07_start"] = df_chisq.case_ma07 - df_chisq.casema07_diff07
    df_chisq["testsma07_start"] = df_chisq.tests_ma07 - df_chisq.testsma07_diff07
    df_chisq["casedet_start"] = df_chisq.case_detrended - df_chisq.casedet_diff07
    df_chisq["casedetpct_start"] = df_chisq.caseDet_pct - df_chisq.casedetpct_diff07
    df_chisq["dt_str"] = df_chisq.Date.dt.strftime("%Y-%m-%d")

    # FIXME


    # df_chisq.set_index(["CountryProv","Date"]).tail()[['case_ma07', 'tests_ma07',  'casema07_diff07', 'testsma07_diff07', 'casema07_start', 'testsma07_start']]

    print("gathering moving 14-day windows")
    #df_sub = df_chisq[df_chisq.Date >= "2020-04-28"]
    df_sub = df_chisq
    df_latest = []
    dtmax_n = df_sub.Date.unique().max()
    dtmin_n = df_sub.Date.unique().min()
    import datetime as dt
    #dt_range = df_sub.Date.unique()
    dt_range = np.arange(dtmax_n, dtmin_n, dt.timedelta(days=-14))
    #dtmax_s = str(dtmax_n)[:10] # http://stackoverflow.com/questions/28327101/ddg#28327650
    for dt_i in dt_range:
      dt_delta = (dt_i - dtmin_n).astype('timedelta64[D]').astype(int)
      if dt_delta < 14: continue
      print(dt_i, dt_delta)

      df_i = df_sub[df_sub.Date <= dt_i]
      df_i = df_i.groupby("CountryProv").apply(lambda g: g.tail(14)).reset_index(drop=True)
      df_i["color"] = "#73b2ff"
      df_i["dtLast"] = dt_i
      df_latest.append(df_i)

    if len(df_latest)==0: raise Exception("No data in moving window")
    df_latest = pd.concat(df_latest, axis=0)
    df_latest["display_cpcode"] = df_latest.apply(lambda g: "" if g.dtLast!=g.Date else g.cp_code, axis=1)
    print("done")

    #source_hist = ColumnDataSource(df_chisq)
    #source_latest = ColumnDataSource(df_latest)

    # since cannot use View iwth LabelSet, creating a different source per continent
    # Couldn't figure out how to filter the datasource in add_layout or Arrow,
    # so just grouping on both continent and dtLast
    srcLatest_continent = df_latest.groupby(["Continent","dtLast"]).apply(lambda g: ColumnDataSource(g))
    srcLatest_continent = srcLatest_continent.reset_index().rename(columns={0:"src"})
    
    plot_size_and_tools = {'plot_height': 300, 'plot_width': 600,
                           'tools':['box_select', 'reset', 'help', 'box_zoom'],
                           'x_axis_type': 'datetime'
                          }
    

    # general-use lines
    slope_y0 = Slope(gradient=0, y_intercept=0, line_color='orange', line_width=50)
    slope_x0 = Slope(gradient=np.Inf, y_intercept=0, line_color='orange', line_width=50)

    # scatter plot
    TOOLTIPS = [
        ("Country/Region", "@CountryProv"),
        ("Date", "@dt_str"),
    ]
    # first set for case vs tests, then second set for case diff vs test diff
    params = (
      #('values', 'tests_ma07', 'case_ma07', 'testsma07_start',  'casema07_start', 'ma07(Tests)', 'ma07(Cases)'),
      #('diffs', 'casema07_diff07', 'testsma07_diff07', 'diff07(ma07(Cases))', 'diff07(ma07(Tests))'),
      ('values', 'case_detrended', 'case_ma07', 'casedet_start',  'casema07_start', 'detrended(cases)', 'ma07(Cases)'),
      #('values', 'caseDet_pct', 'case_ma07', 'casedetpct_start',  'casema07_start', 'detrended(ma07(cases))/cases*100', 'ma07(Cases)'),
    )
    p_all = {'values': [], 'diffs': []}
    from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead
    for k, fdxv, fdyv, fdxs, fdys, labx, laby in params:
      p_cont = []
      for srcCont_i in srcLatest_continent.iterrows():
          srcCont_i = srcCont_i[1]
          print("Adding plot for %s, %s"%(srcCont_i.Continent, srcCont_i.dtLast))

          #init_group=dtmax_s
          #gf = GroupFilter(column_name='dtLast', group=init_group)
          #view1 = CDSView(source=srcCont_i.src, filters=[gf])

          p_d1=figure(plot_width=600,plot_height=400,tooltips=TOOLTIPS,title="%s %s"%(srcCont_i.Continent, srcCont_i.dtLast))

          #p_d1.triangle(fdxv, fdyv, source=srcCont_i.src, size=12, color='blue', angle="angle")
          #p_d1.scatter(fdxs, fdys, source=srcCont_i.src, size=3, color='red') #, view=view1)
          p_d1.scatter(fdxv, fdyv, source=srcCont_i.src, size=3, color='red')
          p_d1.add_layout(
            Arrow(
              end=VeeHead(size=6),
              x_start=fdxs,
              y_start=fdys,
              x_end=fdxv,
              y_end=fdyv,
              line_color='blue',
              source=srcCont_i.src
              #view=view1 # srcCont_i.src
            )#,
            #view=view1 # not supported
          )

          p_d1.xaxis.axis_label = labx
          p_d1.yaxis.axis_label =  laby
          from bokeh.models import LabelSet
          labels = LabelSet(x=fdxv, y=fdyv, text='display_cpcode', level='glyph',
                   x_offset=5, y_offset=5, source=srcCont_i.src, render_mode='canvas')
          p_d1.add_layout(labels)
          p_d1.add_layout(slope_y0)
          p_d1.add_layout(slope_x0)
          p_cont.append(p_d1)

      p_all[k] = p_cont

    # group plots into 3 per row
    # https://stackoverflow.com/a/1625013/4126114
    from itertools import zip_longest
    for k in ['values', 'diffs']:
      p_cont = p_all[k]
      p_cont = list(zip_longest(*(iter(p_cont),) * 3))
      p_cont = [[e for e in t if e != None] for t in p_cont]
      p_all[k] = p_cont

    g = gridplot(p_all['values'] + p_all['diffs'])
    layout = column(g)

    return layout


class GlobalScatterplots:
  def read_csv(self, dir_gitrepo):
    from .p3b_chisquared_detailed import read_csv as read_csv_chisq
    from .p3b_chisquared_detailed import postprocess as postprocess_chisq
    self.df_chisq = read_csv_chisq(dir_gitrepo)
    self.df_chisq = postprocess_chisq(self.df_chisq, dir_gitrepo)

  def create_layout(self):
    self.layout = figure_scatter_values(self.df_chisq)

  def to_html(self, dir_plot_destination):
    fn_dest = join(dir_plot_destination, "p5_global_scatter.html")
    output_file(fn_dest)

    # https://stackoverflow.com/a/46786272/4126114
    # from bokeh.io import curdoc
    # curdoc().title = "COVID-19 Scatter Plots of Cases vs Tests" # FIXME doesnt work
    save(self.layout)
    print(f"Saved to {fn_dest}")

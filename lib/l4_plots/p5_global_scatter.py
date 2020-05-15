from bokeh.models import CDSView, ColumnDataSource, GroupFilter, TapTool, CustomJS, Slope
import pandas as pd
from bokeh.plotting import figure, show, output_file, save
from bokeh.layouts import gridplot, column, row
import numpy as np
from os.path import join



def figure_scatter_values(df_chisq):
    df_chisq["casema07_diff07"] = df_chisq.case_ma07.diff(periods=7)
    df_chisq["testsma07_diff07"] = df_chisq.tests_ma07.diff(periods=7)

    df_latest = df_chisq.groupby("CountryProv").apply(lambda g: g.tail(1)).reset_index(drop=True)
    df_latest["color"] = "#73b2ff"

    source_hist = ColumnDataSource(df_chisq)
    source_latest = ColumnDataSource(df_latest)

    # since cannot use View iwth LabelSet, creating a different source per continent
    srcLatest_continent = df_latest.groupby("Continent").apply(lambda g: ColumnDataSource(g))
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
    ]
    # first set for case vs tests, then second set for case diff vs test diff
    params = (
      ('values', 'case_ma07', 'tests_ma07', 'ma07(Cases)', 'ma07(Tests)'),
      ('diffs', 'casema07_diff07', 'testsma07_diff07', 'diff07(ma07(Cases))', 'diff07(ma07(Tests))'),
    )
    p_all = {'values': [], 'diffs': []}
    for k, fdx, fdy, labx, laby in params:
      p_cont = []
      for srcCont_i in srcLatest_continent.iterrows():
          srcCont_i = srcCont_i[1]
          p_d1=figure(plot_width=600,plot_height=400,tooltips=TOOLTIPS,title=srcCont_i.Continent)
          p_d1.scatter(fdx, fdy,source=srcCont_i.src, size=12,color='color')
          p_d1.xaxis.axis_label = labx
          p_d1.yaxis.axis_label =  laby
          from bokeh.models import LabelSet
          labels = LabelSet(x=fdx, y=fdy, text='cp_code', level='glyph',
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
    save(self.layout)
    print(f"Saved to {fn_dest}")

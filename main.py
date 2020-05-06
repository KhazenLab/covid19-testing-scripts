# -*- coding: utf-8 -*-


from lib.l0_importBiominers import L0ImportBiominers
from lib.l1_importOthers import L1ImportOthers
from lib.l2_mergeTogether import L2MergeTogether
from lib.l3_generateArcData import L3GenerateArcData
from lib.l4_plots import L4Plots


# Enable debug level messages
# I used this section to see debug messages during the l0 run
# Used as: NOTIONPY_LOG_LEVEL=debug LOG_LEVEL=debug python3 main.py ...
# But definitely can be simplified. Anyway, in the end, it was an internet problem
# https://stackoverflow.com/a/16043023/4126114
#import os
#import logging
#logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.propagate = True
#print(os.environ.get("NOTIONPY_LOG_LEVEL"))
#print(os.environ.get("LOG_LEVEL"))
#from notion.logger import enable_debugging
#enable_debugging()
#
#logging.getLogger("requests").setLevel(logging.DEBUG)
#logging.getLogger("notion").setLevel(logging.DEBUG)
#logging.getLogger("requests.packages.urllib3").setLevel(logging.DEBUG)
#logging.getLogger("urllib3").setLevel(logging.DEBUG)
#logging.getLogger("urllib").setLevel(logging.DEBUG)
#
#
#for key in logging.Logger.manager.loggerDict:
#    print(key)
#    logging.getLogger(key).setLevel(logging.DEBUG)



import click
@click.group()
def cli():
    pass


@cli.command()
@click.argument('notion_fn')
@click.argument('fn_biominers')
def l0_importBiominers(notion_fn, fn_biominers):
    """
    Read all the data from the notion.so tables and dump into a csv

    Requires the notion.so unofficial API key

    Original notebook is:
        t11-shadi-collect notion tables of total tests.ipynb
        https://colab.research.google.com/drive/1y0DWBLeLoKfLCw0G0E5QeXa4OdRv228Z
    """
    # notion_fn="notion-shadiakiki1986-token_v2.txt"
    # fn_biominers = "multiple-biominers-gitrepo.csv"
    factory = L0ImportBiominers()
    factory.get_notion_token(notion_fn)
    factory.fetch_tables()
    factory.to_csv(fn_biominers)


@cli.command()
@click.argument('dir_gitrepo')
@click.option("--skip-download", is_flag=True, default=False)
def l1_importOthers(dir_gitrepo, skip_download):
  """
  Read data from other non-biominer sources

  Original notebook at
      t11b-shadi-collect biominers and non-biominers sources.ipynb
      https://colab.research.google.com/drive/1yN-HGiOJzMDXnaimHZ96yUBT7bU38A94
  """

  factory = L1ImportOthers(dir_gitrepo, do_download = not skip_download)

  factory.get_jhu_conf_deaths()
  factory.get_owid_roser()
  factory.get_owid_ortiz()
  factory.get_covidtracking_usa()
  factory.get_wikipedia()
  factory.get_worldometers()
  factory.get_biominers()
  factory.merge_all()
  factory.aggregate_and_to_csv()
  factory.one_field()
  factory.drop_outlaws()
  factory.to_csv_subcols()
  factory.to_csv_all()


@cli.command()
@click.argument('dir_gitrepo')
def l2_mergeTogether(dir_gitrepo):
  """
  Merge tests data with confirmed cases data and population
  
  From notebook: t11c2-shadi-merge with confirmed cases and population.ipynb

  Automatically generated by Colaboratory.

  Original file is located at
    https://colab.research.google.com/drive/1XeMityBlecPV8kyatsoIy82Zml8qyr8Y
  """
  factory = L2MergeTogether(dir_gitrepo)
  factory.read_confirmed_cases()
  factory.read_totaltests()
  factory.merge_conf_total()
  factory.drop_outlaws()
  factory.merge_country_meta()
  factory.export_count_per_source()
  factory.add_supplementary_stats()
  factory.to_csv_historical()
  factory.to_csv_latestOnly()


@cli.command()
@click.argument('dir_gitrepo')
def l3_generateArcData(dir_gitrepo):
  """
  Convert data from l2 csv files into format suitable for our dashboard on arcgis.com
  """
  factory = L3GenerateArcData(dir_gitrepo)
  factory.read_l2_historical()
  factory.calculate_stats()
  factory.write_latest()
  factory.write_dailyStacked()
  factory.write_chisquared()


@cli.command()
@click.argument('csv_l2_historical')
@click.argument('dir_plot_destination')
def l4_plots(csv_l2_historical, dir_plot_destination):
  """
  Generate plots, eg figure of stacked number of countries/states per day per source
  """
  factory = L4Plots()
  factory.read_csv(csv_l2_historical)
  factory.prep_plots()
  factory.plot_line(dir_plot_destination)
  factory.plot_stacked(dir_plot_destination)


if __name__ == '__main__':
    cli()

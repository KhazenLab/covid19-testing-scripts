# -*- coding: utf-8 -*-


from .l0_importBiominers import L0ImportBiominers
from .l1_importOthers import L1ImportOthers


import click
@click.group()
def cli():
    pass


@cli.command()
@click.argument('notion_fn')
@click.argument('fn_biominers')
def l0_importBiominers(notion_fn, fn_biominers):
    """
    Original notebook is:
        t11-shadi-collect notion tables of total tests.ipynb
        https://colab.research.google.com/drive/1y0DWBLeLoKfLCw0G0E5QeXa4OdRv228Z

    Read all the data from the notion.so tables and dump into a csv

    Requires the notion.so unofficial API key
    """

    # notion_fn="notion-shadiakiki1986-token_v2.txt"
    # fn_biominers = "multiple-biominers-gitrepo.csv"
    factory = L0ImportBiominers(self, notion_fn, fn_biominers)
    factory.get_notion_token(notion_fn)
    factory.fetch_tables()
    factory.to_csv(fn_biominers)


@cli.command()
@click.argument('dir_gdrive')
def l1_importOthers(dir_gdrive):
    """
    Original notebook at
        t11b-shadi-collect biominers and non-biominers sources.ipynb
        https://colab.research.google.com/drive/1yN-HGiOJzMDXnaimHZ96yUBT7bU38A94

    Read data from other non-biominer sources
    """

  dir_gdrive = "/content/covid19-testing"
	factory = L1ImportOthers(dir_gdrive)

  factory.get_owid_roser()
  factory.get_owid_ortiz()
  factory.get_wikipedia()
  factory.get_worldometers()
  factory.get_biominers()
  factory.merge_all()
  factory.aggregate_and_to_csv()
  factory.one_field()
  factory.to_csv_subcols()
  factory.to_csv_all()


if __name__ == '__main__':
    cli()

# -*- coding: utf-8 -*-


from .l0_importBiominers import L0ImportBiominers


import click

@click.command()
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


if __name__ == '__main__':
    l0_importBiominers()

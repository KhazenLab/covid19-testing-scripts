# -*- coding: utf-8 -*-
"""
Original notebook is:
    t11-shadi-collect notion tables of total tests.ipynb
    https://colab.research.google.com/drive/1y0DWBLeLoKfLCw0G0E5QeXa4OdRv228Z

Read all the data from the notion.so tables and dump into a csv

Requires the notion.so unofficial API key
"""

import pandas as pd
from notion.client import NotionClient

from .lib import get_table, postprocess_table


fn="notion-shadiakiki1986-token_v2.txt"
token_v2=open(fn,"r").read().strip()
client = NotionClient(token_v2=token_v2)


# get all
df_global = []
for country_name in notion_map.keys():
  print(country_name)
  df_single = get_table(client, country_name)
  print("%s .. %s"%(country_name, df_single.shape))

  df_single = postprocess_table(country_name, df_single)
  # df_single = df_single[["Date","total_cumul"]]

  df_single["country_t11"] = country_name
  df_global.append(df_single)

# merge
df_global = pd.concat(df_global, axis=0)
df_global = df_global.loc[pd.notnull(df_global.total_cumul),]
df_global = df_global.sort_values(["country_t11", "Date"], ascending=True)

# save
fn_biominers = "multiple-biominers-gitrepo.csv"
df_save = df_global[["country_t11", "Date", "total_cumul"]]
df_save.to_csv(fn_biominers, index=False)

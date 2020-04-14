notion_map = {
    # Maintainer = Shadi
    "Armenia": "https://www.notion.so/59b0c69000274ff1b1ee83c0c6cea5a0?v=b6a8a7f3941c47ecae19ffe621482f59",
    "Austria": "https://www.notion.so/6d378966ff5c4e268376627f86f4dc2f?v=0dacaca7b49c4700a49efa550fb5f6c2",
    "Bahrain": "https://www.notion.so/9c9f2c905ae545faacaf13071d2eb033?v=7fe7cb6968bc42818030a583bac34998",
    "Colombia": "https://www.notion.so/2461e76d09cf4f05a7278a20ff1bf279?v=6233265e684a44be8a2b570b4ad7a028",
    "Costa Rica": "https://www.notion.so/1fbb092cfc1647e9a6742b54a106d13a?v=91a240e759c5406d9f2b274ad692b1ab",
    "Croatia": "https://www.notion.so/90ba2ccb229240918edce09e52ee9030?v=f28a379e24c94a3a939a7e4d891e452b",
    "Estonia": "https://www.notion.so/02011176912449ec83155233a9fbc1d7?v=7c0c40d9b4764fbd82ea999cfe529fa4",
    "Japan": "https://www.notion.so/7ac8794671464e1bbbb5b6c8ddc279f4?v=e6c39cb9ec8142939ab017c33b5aa969",
    "Jordan": "https://www.notion.so/3d290d580fa5438cbefb4f6c7d2fc375?v=fb6da0a4a57f4236b3c528fd1e9c4ad5",
    "Lebanon": "https://www.notion.so/16670cd6b914491ebfc2b488ef1b9e89?v=b0b003183b814c33830396970fac5187",
    "Philippines": "https://www.notion.so/41f843de416c4f41b9266781361e5fdb?v=842f654ed1004b6f9022421bfce6c6d6",

    # Halim
    "Argentina": "https://www.notion.so/a09b8d4dd2c44745983ab1916445ed94?v=266d332fc93543069857c1f081ea37a6",
    "Australia":  "https://www.notion.so/519b9667ab114786be8be3b1a2306c68?v=14f86820859d48be8cbc5a3199392d25",
    "Azerbaijan": "https://www.notion.so/f587f06c442b45f09c7be0ac3f58f514?v=f73a7b62fe6b4de8ac0a6f818d5a8274",
    "Bangladesh": "https://www.notion.so/35b7ee1e86b643ef8b64417112858405?v=ecbfa792b75947c6bf21501e28bf50cd",
    "Bolivia": "https://www.notion.so/9214e05323bb48f18817ed86125cf2c0?v=f3f10addeaa94d5fafbf8a5dd543ddcc",
    "Bosnia and Herzegovina": "https://www.notion.so/c4d504fb061d4a2e8d1e9b4eef16f8db?v=082817d19e1746ccbe9f98999752ddb5",
    "Chile": "https://www.notion.so/5b5ff55b44c84f09ba89d9e0bb5fd834?v=84f03e51051c41579958fc2054ff2c35",
    "Hungary": "https://www.notion.so/891f5d09165d4815834921adf73a673e?v=210fc8fb1d6a4bc297b1c5ec193ca7e1",
    "Indonesia": "https://www.notion.so/f9b8def063b14688bea0731ccb5dc046?v=464fba9d406a4d708a4c8274e44804f8",
    "New Zealand": "https://www.notion.so/66ea1fa7a90c4ff481e5c0eb6573ba67?v=a84dbac7dd2e422d93557007d1c5eaa1",
    "Northern Macedonia": "https://www.notion.so/7bba8f1ac34e43e19ff42f3d331c406d?v=6e85b5a16122473194ebcb7d1d3080a1",
    "Serbia": "https://www.notion.so/64ebd94f97d3440ca3431d9dd4850f76?v=05b88d514b6641d9a01da44a31372f7c",
    "Slovenia": "https://www.notion.so/200f4d913065463a92bdd8e009616af4?v=ed8aecb1b5354c6d905bfe8b5721ff90",
    "South Africa": "https://www.notion.so/e7be19dda46349188a998c7feb7c861c?v=457a2e1ffc514b4b9ebb59c626711b67",
    "Uruguay": "https://www.notion.so/d9f406529d9e4b0aa000c5950e05779f?v=67daa5dc0deb40869780016b2fa62e22",
    "Vietnam": "https://www.notion.so/c20b8220238c4fab8b183b3ee8276603?v=b4382f1d9c4e4d74b7c05b1fcd9183aa",
}


from notion.collection import NotionDate
import pandas as pd


def get_table(client, country_name):
    if not country_name in notion_map.keys():
      raise Exception(f"Country %{country_name} not found in notion map")

    page = client.get_block(notion_map[country_name])
    coll=page.collection.get()

    # column names, eg ['deaths', 'treatment', 'confirmed', 'negative', 'recoveries', 'Date', 'ID']
    colnames = [x['name'] for i,x in coll['schema'].items()]
    
    # prep for dataframe
    rows = page.collection.get_rows()
    df_all = []
    for i,r in enumerate(rows):
      df_new = {}
      for c in colnames:
        v = getattr(r,c)
        if type(v)==NotionDate: v = v.start
        df_new[c] = v

      df_all.append(df_new)
      #print(i, c, r[c])

    # actual dataframe
    df_all = pd.DataFrame(df_all)

    return df_all


def postprocess_table(country_name, df_single):
  # Update 2020-04-09: in general, do not replace NA with 0 with fillna(0)

  if country_name=="Argentina":
    # df_single["total_cumul"] = df_single[["neg cumul labs", "neg cumul epid", "confirmed cumulative"]].fillna(0).apply(sum, axis=1)
    # Update 2020-04-09: do not use neg cumul epid
    df_single["total_cumul"] = df_single[["neg cumul labs", "confirmed cumulative"]].apply(sum, axis=1)
    return df_single
  
  if country_name=="Armenia":
    df_single["total_cumul"] = df_single[["confirmed", "negative"]].apply(sum, axis=1)
    return df_single

  if country_name=="Bolivia":
    df_single["total_cumul"] = df_single[["cumulative negative", "cumulative confirmed"]].apply(sum, axis=1)
    return df_single

  # Update 2020-04-10: turns out they have a total cumulative tests field
  # Update 2020-04-14: Halim dropped the total field and is just recording positive and negative
  if country_name=="Bosnia and Herzegovina":
    df_single["total_cumul"] = df_single[["negative_cumul", "positive_cumul"]].apply(sum, axis=1)
    return df_single

  if country_name=="Colombia":
    df_single["total_cumul"] = df_single[["confirmed cumul", "negative cumul"]].apply(sum, axis=1)
    return df_single

  if country_name=="Costa Rica":
    df_single["total_cumul"] = df_single[["confirmed cumul", "negative cumul"]].apply(sum, axis=1)
    return df_single

  #if country_name=="Croatia":
  #  # Croatia has a total_cumul column, but for some dates that are missing it, we can calculate it from confirmed + negative
  #  df_single["total_cumul"] = df_single[["confirmed cumul", "negative cumul"]].fillna(0).apply(sum, axis=1)
  #  return df_single

  # Update 2020-04-09: just use the total_cumul field directly
  #if country_name=="Estonia":
  #  df_single["total_cumul"] = df_single[["confirmed", "negative"]].apply(sum, axis=1)
  #  return df_single

  if country_name=="Philippines":
    df_single["total_cumul"] = df_single[["confirmed", "negative"]].apply(sum, axis=1)
    return df_single

  if country_name=="Vietnam":
    df_single["total_cumul"] = df_single[["total positive", "total negative"]].apply(sum, axis=1)
    return df_single

  print(f"no postprocessing for country {country_name}")
  return df_single



import pandas as pd
from notion.client import NotionClient

class L0ImportBiominers:

  def get_notion_token(self, notion_fn):
    token_v2=open(notion_fn,"r").read().strip()
    self.client = NotionClient(token_v2=token_v2)

  def fetch_tables(self):
    # get all
    df_global = []
    for country_name in notion_map.keys():
      print(country_name)
      df_single = get_table(self.client, country_name)
      print("%s .. %s"%(country_name, df_single.shape))

      df_single = postprocess_table(country_name, df_single)
      # df_single = df_single[["Date","total_cumul"]]

      # At this point, all tables should have a total_cumul field and a Date field
      # whether it comes from the notion.so table directly, or from the postprocess_table function
      assert "Date" in df_single.columns
      assert "total_cumul" in df_single.columns

      df_single["country_t11"] = country_name
      df_global.append(df_single)

    # merge
    df_global = pd.concat(df_global, axis=0)
    df_global = df_global.loc[pd.notnull(df_global.total_cumul),]
    df_global = df_global.sort_values(["country_t11", "Date"], ascending=True)
    self.df_global = df_global

  def to_csv(self, fn_biominers):
    # save
    # fn_biominers = "multiple-biominers-gitrepo.csv"
    df_save = self.df_global[["country_t11", "Date", "total_cumul"]]
    df_save.to_csv(fn_biominers, index=False)



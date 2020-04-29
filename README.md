# covid19-testing-scripts

Scripts that process data from/into the git repo `covid19-testing-data`



## Installation

```
pip3 install pew
pew new biominers_covid19
pip3 install notion pandas Click
```

where `notion` is the "Unofficial Python API client for Notion.so" from https://github.com/jamalex/notion-py/
also mentioned at https://www.notion.so/Notion-Hacks-27b92f71afcd4ae2ac9a4d14fef0ce47


It also helps to see CSVs in the terminal with vd:

```
pip3 install visidata
```

## Usage

Step 0: import notion tables

- This requires the notion token, as documented at https://github.com/jamalex/notion-py/
- The exact documentation from that page of how to get this is:

    Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so"

- In Chrome, this means: More tools, Developer tools, Application, Cookies, notion.so, `token_v2` value
  - and save that into a txt file
- Also, in notion, you need to have your own workspace (other than the workspace in which the tables exist)


Command to run step 0:

```
python3 main.py l0-importbiominers \
    path/to/notion/key.txt \
    ~/Development/gitlab.com/biominers/covid19-testing-data/l0-notion_tables/multiple-biominers-gitrepo.csv 
```

To display more verbose logging during the l0 step, check related notes in main.py


Step 1: import non-biominer tables and merge with biominer

(This includes ourworldindata.org, wikipedia, and worldometers)

```
python3 main.py l1-importothers \
  ~/Development/gitlab.com/biominers/covid19-testing-data/
```


Step 2: merge with confirmed cases

(TODO add extracting the latestOnly file as well)

```
python3 main.py l2-mergetogether \
  ~/Development/gitlab.com/biominers/covid19-testing-data/
```


Step 3: interpolate and extrapolate

```
python3 main.py l3-generatearcdata \
  ~/Development/gitlab.com/biominers/covid19-testing-data/
```


After running step 3, we currently need to open all the `ArcGIS/v2/*csv` files manually in excel/libreoffice and resave the csv to drop the `.0` suffixes of decimals.

Casting the corresponding dataframe column to int doesnt work because it contains NAs, which cannot coexist in int column in pandas


## Shiny apps

The first shiny app was created for the comparison of different countries.

It's committed in this repo at `shinyScripts/compareCountries/compareCountries.R`

Follow instructions in the fil header there.

# covid19-testing-scripts

Scripts that process data from/into the git repo `covid19-testing-data`



## Installation

```
pip3 install pew
pew new biominers_covid19
pip3 install notion pandas Click requests_cache==0.5.2
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
- Finally, note that if the l0 step is giving an "unauthorized" error, check if your token needs updating


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

or add `--skip-download` to avoid downloading JHU, OWID, etc


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


## Data cleaning

### Part 1: daily tests being negative

We first started doing data cleaning inline in the source code.
Then we started complementing that with a `drop_entries.csv` file in the data repo,
which we read here in the CLI.
The way the `drop_entries.csv` file was built is by opening the `l1b/side-by-side.csv` file in a worksheet editor,
then adding 2 columns to it:

- neg diff: in K2 then drag down:

`=IF(A2=A1, IF(I2-I1<0, "x", ""), "")`

- diff with context: in L21 then drag down:

`=IF(OR(K21="x", K20="x", K19="x", K18="x", K17="x", K16="x", K22="x", K23="x", K24="x", K25="x", K26="x"), "y", "")`

Then I filter the sheet for `diff with context = y`.

Finally I add a `drop row` column which I manually annotate with `d` for rows that I inspect and decide to drop.
Sometimes I drop the row marked with `neg diff=x`, othertimes it's the rows before or after it.
If it's a biominers entry, then I fix the issue in the notion tables.

I finally save it as `drop_entries.csv` for example in the data repo.

For future rows that also need to be dropped, I will need to concatenate the newly done file above with the existing one in the repo.

Update: Adding new batch of data cleaning now.
First, I sort by Location, Date, source.
Then I add a new column `dupe` with `=IF(AND(A2=A1,B2=B1,J2=J1), IF(M2="d",IF(M1<>"d", "important", "candel"), "candel"), "")` in the `drop_entries.csv` file
after I pasted the new rows to be dropped.
Then I needed to mark the row above the dupe with "d" since I need to delete the dupe rows.
Finally I delete all the rows marked with "candel", drop the dupe column, and save to csv.


## Part 2: daily tests less than daily confirmed

## Part 2a: due to extended data

Saved in `l0/drop_tests_lessthan_confirmed.csv'

Based on `l2/t11c-confirmed+totalTests-historical.csv`, and prioritized in notebook t11d in the section that highlights countries with tests less than confirmed < -1k for example

Procedure
- rename CountryProv to Location, `total_cumul.source` to source
- add `d conf` and `d test` and `test - conf` columns for info
- mark `drop row` manually
- set in S4 formula `=IF(OR(R4="d",R3="d",R2="d",R5="d",R6="d"), "x", "")` to get some context
- drop everything that has empty in the context
- drop unnecessary columns

## Part 2b: due to linear interpolation mismatch with concave confirmed cases

Data from notion table `Artificial biominers data` (Link: https://www.notion.so/Artificial-biominers-data-dabae264d80b4c8fb9f7751730c05632 )

Check also the section `Data cleaning` (link: https://www.notion.so/Testing-Statistics-Data-Collection-c9ee53ecacfc4eee950fcc466b8dfb72#1ae3ae9a07d04bb891084702d1bbae9a )

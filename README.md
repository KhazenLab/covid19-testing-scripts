# covid19-testing-scripts

Scripts that process data from/into the git repo `covid19-testing-data`



## Installation

```
pip3 install pew
pew new biominers_covid19
pip3 install notion pandas Click requests_cache==0.5.2 seaborn==0.10.1 matplotlib==2.1.2 statsmodels==0.11.1
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
rm demo_cache.sqlite
python3 main.py l1-importothers \
  ~/Development/gitlab.com/biominers/covid19-testing-data/
```

or add `--skip-download` to avoid downloading JHU, OWID, etc

Check the related section `Troubleshooting / How to deal with l1 error "Found 46 triplets with dips in their cumulative tests."`


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


Step 4a: Notebook t11d: R, chisquared thresholds.

- input: `l2/interpolated.csv`
- outputs:
  - `l4/t11d-chisquared-history-v20200512.csv`
  - deprecated: `l2/t11d-chisquared-ranks.csv`


Step 4b: perform analysis and generate plots

- input: `l4/t11d-chisquared-history-v20200512.csv`
- output: `l4/chisquared-postprocessed.csv` and other l4 html files

```

python3 main.py l4-plots \
  ~/Development/gitlab.com/biominers/covid19-testing-data/ \
  www/
```

Upload plots to AWS S3 bucket as static html

```
AWS_PROFILE=shadi_shadi aws s3 sync www/ s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read

# or for uploading a single file
AWS_PROFILE=shadi_shadi aws s3 cp www/t11d-chisquared_dashboard-simple.html s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
```

If the `--acl` doesn't work (it works as of 2020-05-12), then make the folder public manually in aws web console.

(https://github.com/aws/aws-cli/issues/1560)


Step 5: generate latest country table

- input: `/ArcGIS/v2/t11c-confirmedtotalTests-latestOnly.csv`
- output: `www/t11c-country_latest_table.html`

```

python3 main.py l5-generatetable \
  ~/Development/gitlab.com/biominers/covid19-testing-data/ \
  www/
```

Upload html table to AWS S3 bucket as static html




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

### Part 2a: due to extended data

Saved in `l0/drop_tests_lessthan_confirmed.csv'

Based on `l2/t11c-confirmed+totalTests-historical.csv`, and prioritized in notebook t11d in the section that highlights countries with tests less than confirmed < -1k for example

Procedure
- rename CountryProv to Location, `total_cumul.source` to source
- add `d conf` and `d test` and `test - conf` columns for info
- mark `drop row` manually
- set in S4 formula `=IF(OR(R4="d",R3="d",R2="d",R5="d",R6="d"), "x", "")` to get some context
- drop everything that has empty in the context
- drop unnecessary columns

### Part 2b: due to linear interpolation mismatch with concave confirmed cases

Data from notion table `Artificial biominers data` (Link: https://www.notion.so/Artificial-biominers-data-dabae264d80b4c8fb9f7751730c05632 )

Check also the section `Data cleaning` (link: https://www.notion.so/Testing-Statistics-Data-Collection-c9ee53ecacfc4eee950fcc466b8dfb72#1ae3ae9a07d04bb891084702d1bbae9a )



## Troubleshooting

### How to deal with l1 error "Found 46 triplets with dips in their cumulative tests."

Here is the current output from l1 while running it on the morning of 05-28

```
# python3 main.py l1-importothers   ~/Development/gitlab.com/biominers/covid19-testing-data/
JHU .. downloading
Download: jhu confirmed global to /tmp/tmpetigqxb6/jhu-global-original.csv: start
Download: jhu confirmed global: end
Download: jhu confirmed usa to /tmp/tmpetigqxb6/jhu-usa-original.csv: start
Download: jhu confirmed usa: end
Download: jhu death global to time_series_covid19_deaths_global.csv: start
Download: jhu death global: end
Download: jhu death usa to time_series_covid19_deaths_US.csv: start
Download: jhu death usa: end
JHU .. done
Download: owid live to /tmp/tmpx2bxxoa6/ourworldindata.org-roser-live.csv: start
Download: owid live: end
Download: cov usa daily to /tmp/tmpx2bxxoa6/covidtracking.com-states_daily.csv: start
Download: cov usa daily: end
Download: cov usa info to /tmp/tmpx2bxxoa6/covidtracking.com-states_info.csv: start
Download: cov usa info: end
Found duplicates in wiki data
Found 46 triplets with dips in their cumulative tests. Here are the top 20:
source            Location       Date total_cumul.source  total_cumul.all  is_wrong  is_approved
1565                Brazil 2020-05-27       worldometers         871839.0      True         True
3300                  Cuba 2020-05-27       worldometers          97003.0      True         True
3359                Cyprus 2020-05-27       worldometers         103814.0      True         True
3482               Czechia 2020-05-27       worldometers         410777.0      True         True
3793    Dominican Republic 2020-05-27       worldometers          70972.0      True         True
4016               Estonia 2020-05-27       worldometers          78085.0      True         True
4218               Finland 2020-05-27       worldometers         171575.0      True         True
4581               Georgia 2020-05-26       worldometers          49093.0      True         True
4655               Germany 2020-05-19               wiki        3595059.0      True        False
4708                 Ghana 2020-05-26       worldometers         197194.0      True         True
5199               Iceland 2020-05-27       worldometers          59087.0      True         True
5795             Indonesia 2020-05-22         owid/roser         168969.0      True        False
6724                 Japan 2020-04-26               wiki         244978.0      True        False
6754                 Japan 2020-05-26       worldometers         435412.0      True         True
6755                 Japan 2020-05-27       worldometers         276170.0      True         True
8301               Myanmar 2020-05-24       worldometers          17875.0      True         True
8515           Netherlands 2020-05-19       worldometers         297347.0      True         True
8895       North Macedonia 2020-05-27       worldometers          25841.0      True         True
9314                  Peru 2020-05-22         owid/roser         112353.0      True        False
9317                  Peru 2020-05-25         owid/roser         123549.0      True        False

      WARNING: Please mark approved (or fix) in l1b-altogether/dropped_outlaws_l1.csv then re-run l1 to re-calculate selected source per country/state/date triplet
            Hint: by default, we mark worldometers drops as approved
```

The download lines are just informative, so there's nothing to do about them ATM.

The line `Found duplicates in wiki data` should be fixed in the wiki data, but we're just ignoring it for now as we are skipping duplicates in the code.

The line `Found 46 triplets with dips in their cumulative tests. Here are the top 20:` is important, and this section describes how to deal with it.

The entries with `is_approved=True` are entries that don't need any action. These are related to the hint below that says "Hint: by default, we mark worldometers drops as approved".

Focusing on the entries with `is_approved=False`, here's a copy of the table above, but filtered for them:

```
Found 46 triplets with dips in their cumulative tests. Here are the top 20:
source            Location       Date total_cumul.source  total_cumul.all  is_wrong  is_approved
4655               Germany 2020-05-19               wiki        3595059.0      True        False
5795             Indonesia 2020-05-22         owid/roser         168969.0      True        False
6724                 Japan 2020-04-26               wiki         244978.0      True        False
9314                  Peru 2020-05-22         owid/roser         112353.0      True        False
9317                  Peru 2020-05-25         owid/roser         123549.0      True        False

      WARNING: Please mark approved (or fix) in l1b-altogether/dropped_outlaws_l1.csv then re-run l1 to re-calculate selected source per country/state/date triplet
            Hint: by default, we mark worldometers drops as approved
```

So we edit the file `l1b-altogether/dropped_outlaws_l1.csv` and look for the entries marked as `is_wrong=True` and examine each of the entries above.

In the case of Germany above, we observe the following from the csv file:

```
Germany,2020-05-10,owid/roser,3177307.0,,
Germany,2020-05-17,owid/roser,3608189.0,,
Germany,2020-05-19,wiki,3595059.0,x,
Germany,2020-05-21,worldometers,3595059.0,,
Germany,2020-05-24,owid/roser,3952971.0,,
Germany,2020-05-28,worldometers,3952971.0,,
```

The first observation is that this dataset is coming from OWID (our top priority source), as well as from wikipedia and worldometers (lower priority sources).
The problem is that the wiki entry on 05-19 (3595059) is smaller than the owid entry on 05-17 (3608189).
To fix this issue, we mark the wiki entry on 05-19 with an x in the last column (i.e. the `is_approved` column) as follows

```
Germany,2020-05-19,wiki,3595059.0,x,x
```

We also notice that the worldometers entry on 05-21 is just a copy of the wiki entry, and hence also has the same problem above.
Therefore, we also mark the worldometers entry with an x in the `is_approved` column as follows

```
Germany,2020-05-21,worldometers,3595059.0,,x
```

With the above 2 approvals, we re-run the `l1` step.
It is not necessary that the `Germany` row on 05-19 disappear from the table of the error message.
The reason is that once we marked the wiki entry above for Germany on 05-19 as skipped,
a re-run of the l1 step will try to fetch that specific date from a lower-priority datasource.
In this case, only worldometers is lower priority than wikipedia, so if worldometers had an entry for Germany on 05-19,
then it would show up in the dataset, and if worldometers had the same problem of being smaller than the owid value on the previous date,
then it would show up again in the table as another row that needs to be skipped.
In reality, worldometers didn't have an entry for Germany on 05-19, so the `Germany` row on 05-19 disappeared from the table of the error message.

Naturally, the other countries would still appear, as we haven't fixed anything about them yet.

Repeating the above procedure for the rest of these countries will lead us to the l1 step running without an error about "dips in cumulative tests".

Note that the l1 step will need to be run multiple times, iterating between running it and editing the `l1b-altogether/dropped_outlaws_l1.csv` file.
The number of times it needs to be run depends on how many new problems show up in the data with the data updates.

Here is the example of Indonesia with an excerpt of the file `l1b-altogether/dropped_outlaws_l1.csv` file

```
Indonesia,2020-05-19,owid/roser,147799.0,,
Indonesia,2020-05-20,owid/roser,154139.0,,
Indonesia,2020-05-21,worldometers,211883.0,,
Indonesia,2020-05-22,owid/roser,168969.0,x,
Indonesia,2020-05-23,owid/roser,176035.0,,
```

In this case, we see that the `is_wrong` field marked with the x is the owid on 05-22.
However, a visual inspection shows that the real problem is in worldometers data on 05-21 in the row before.
In this case, the solution is to mark the worldometers row on 05-21 as approved to skip instead of the owid row on 05-22.

Occasionally, there are trickier cases, such as Philippines showing up in this error table.
The problem for Philippines is that it was being fetched by us, and OWID started fetching it later.
The prioritization starts picking up data for Philippines from OWID, and it finds that OWID's data is not at the same level of ours (i.e. biominers),
so it shows errors in the data for several dates, including past dates from April which would normally have already been treated as of 05-28.

Here is the current excerpt of Philippines to illustrate my point

```
Philippines,2020-04-07,biominers,32315.0,,
Philippines,2020-04-08,biominers,35335.0,,
Philippines,2020-04-09,biominers,37324.0,,
Philippines,2020-04-10,biominers,38568.0,,
Philippines,2020-04-11,owid/roser,33783.0,x, <<<< first row showing that OWID data at 33k is not inline with our own (biominers) data at 38k
Philippines,2020-04-12,biominers,41580.0,,
Philippines,2020-04-13,owid/roser,38058.0,x, <<< another problem since 38k is a drop from 41k
Philippines,2020-04-14,owid/roser,39898.0,,
Philippines,2020-04-15,owid/roser,42173.0,,
Philippines,2020-04-16,biominers,51911.0,,
Philippines,2020-04-17,owid/roser,49571.0,x,
Philippines,2020-04-18,owid/roser,52792.0,,
Philippines,2020-04-19,biominers,61306.0,,
Philippines,2020-04-20,biominers,63629.0,,
Philippines,2020-04-21,owid/roser,60944.0,x,
Philippines,2020-04-22,owid/roser,64475.0,,
Philippines,2020-04-23,owid/roser,68649.0,,
Philippines,2020-04-24,owid/roser,72657.0,,
Philippines,2020-04-25,owid/roser,75902.0,,
Philippines,2020-04-26,biominers,86305.0,,
Philippines,2020-04-27,biominers,90733.0,,
Philippines,2020-04-28,owid/roser,88869.0,x,
Philippines,2020-04-29,owid/roser,93387.0,,
Philippines,2020-04-30,owid/roser,97349.0,,
Philippines,2020-05-01,owid/roser,103472.0,,
Philippines,2020-05-02,biominers,114125.0,,
Philippines,2020-05-03,owid/roser,113333.0,x,
Philippines,2020-05-04,owid/roser,119512.0,,
Philippines,2020-05-04,worldometers,120736.0,x,x
Philippines,2020-05-05,owid/roser,126387.0,,
Philippines,2020-05-06,owid/roser,131490.0,,
Philippines,2020-05-06,worldometers,132689.0,x,x
Philippines,2020-05-07,owid/roser,136706.0,,
Philippines,2020-05-08,biominers,146685.0,,
Philippines,2020-05-09,wiki,163177.0,,x
Philippines,2020-05-09,worldometers,151080.0,x,x
Philippines,2020-05-10,wiki,173144.0,,x
Philippines,2020-05-11,biominers,171086.0,,
Philippines,2020-05-11,wiki,181668.0,,x
Philippines,2020-05-12,owid/roser,171608.0,,
Philippines,2020-05-12,worldometers,173352.0,x,x
Philippines,2020-05-13,owid/roser,184617.0,,
Philippines,2020-05-13,worldometers,181668.0,,x
Philippines,2020-05-14,biominers,199205.0,,
Philippines,2020-05-14,worldometers,188649.0,,x
Philippines,2020-05-15,owid/roser,188024.0,x,
Philippines,2020-05-16,biominers,219224.0,,
Philippines,2020-05-17,biominers,228319.0,,
Philippines,2020-05-18,biominers,233713.0,,
Philippines,2020-05-19,biominers,240482.0,,
Philippines,2020-05-19,worldometers,244800.0,x,x
Philippines,2020-05-20,biominers,247967.0,,
Philippines,2020-05-21,worldometers,259172.0,x,x
```

There are many ways to go about the above, but we try to be systematic by giving priority to OWID data, so the solution that we follow is to mark the biominers rows as skipped.

Here is another example of a problem from covidtracking.com

```
US – District of Columbia,2020-05-21,covidtracking.com,41756.0,,
US – District of Columbia,2020-05-22,covidtracking.com,42993.0,,
US – District of Columbia,2020-05-23,covidtracking.com,51991.0,,
US – District of Columbia,2020-05-24,covidtracking.com,51991.0,,
US – District of Columbia,2020-05-25,covidtracking.com,40803.0,x,
US – District of Columbia,2020-05-26,covidtracking.com,42055.0,,
US – District of Columbia,2020-05-27,covidtracking.com,42697.0,,
```

Eventhough the row marked as offending is the 05-25 one with 40k being a drop from 51k,
the cleaner solution in this case is to mark the 51k as skipped, that way only 05-23 and 05-24 are skipped,
instead of having to skip 05-25, 05-26, 05-27, and possibly later dates.
Note that we should also skip the 05-22 date, otherwise it is still offending wrt to 05-26.

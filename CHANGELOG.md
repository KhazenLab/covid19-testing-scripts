All entries in reverse chronological order.


Version 0.9 (2020-05-??)

- feat, l4: distinguish p3 slopes fig from p4 chi-squared plots and merge together
- enh, l4: chisquared detail plots to have region
- enh, l4: chisquared + scatter of slopes improved aesthetics
- enh, l4: chisquared added aggregates by world, continents
- enh, l4: p3a chisquared+trends: html responsive
- enh, l4: spin off p3a (simplified) and p3b (detailed) out of p3
- enh, l4: chisquared step now saves the postprocessed csv into the data repository


Version 0.8 (2020-05-13)

- feat, l4: add command l4-plots to generate plots from publication 1
- feat, l2: interpolation in tests by translate + scale from the number of confirmed cases
  - This ensures that the daily number of tests is always greater than or equal to the number of confirmed cases
- feat, l1+l2: split out common code for adding context to boolean column
- feat, l2: incorporate manually-done datacleaning of confirmed cases + add check that no negatives
- enh, l2: improvements to the interpolation after testing in notebook
- feat, l2: drop spikes by easing (from notebook t15b)
- enh, l0: add brazil
- feat, l4: add static html dashboard built with bokeh for postprocessing data
- feat, www: create a new www folder that can be synced to s3 as our internal dashboard
- feat, l4: add spike easing to confirmed cases, make spike easing more strict
  - bugfix: found that some cases were yielding dips, so I added a workaround for those, but it's not a full fix though
- feat, l4: integrate chi-squared dashboard
- bug, l0: san marino needs summation of total cumul fields
- enh, l1: add warning if wiki floats are strings
- enh, l4: plots down to 100 dpi for sharing on the internal dashboard (from 300 dpi for print)


Version 0.7 (2020-05-06)

- feat, l1: start using `drop_entries.csv` for datacleaning
- enh, l0: abort if duplicates in biominers data
- enh, l1: wiki and worldometers had nans, dropped
- bug, l1: covidtracking.com updated urls
- feat, l1: start using `l0/drop_tests_lessthan_confirmed.csv` for datacleaning
- feat, l3: start using interpolation by transformation
- enh, l1: more data cleaning (done in code, but will do in `l0/drop_entries.csv` later, by Halim)
- enh, l0: new countries from notion
- bug, l1: fix expiry setting on cache
- enh, l1: convert exception to warning when dips are found + calculate diff on non-na's
- bug, l2: renames of countries that already exist. Injected a check about it
- feat, l1+l2: CLI outputs l1/drop and l2/drop with enough fields to perform the datacleaning without needing to vimdiff with other csv files
- enh, l0: cambodia table column got renamed
- feat, l1: add skip-download option
- enh, l0: moved some renames from l2 to l0


Version 0.6 (2020-04-29)

- enh, l3: drop the outdated R scripts
- enh, l3: overwrite negative values with 0
- bug, l1: data cleaning of numbers causing negative values
- bug, l1: owid live had duplicates which showed up when added the UID field for data cleaning. Fixed
- feat, l1: add caching for 1 hour for JHU and OWID live files
- bug, l1: drop using the owid frozen version. Check comments in function for more details
- enh, l1: more worldometers country name corrections
- enh, l1: worldometers using non-utf8 encoding in read csv
- enh, l1: worldometers drop extended values


Version 0.5 (2020-04-27)

- 2020-04-27
	- l0 added 5 country/state entries from students
  - compareCountries Initial commit
  - l3 fix
  - l1 fix for nova scotia
  - l3 added 2 new columns to historical and removed some visually weird data
  - l0 added faroe islands
- 2020-04-25
  - l0 handle different columns in UK channel Islands
  - l1 dropped jersey as api is not helpful
  - l0 fix to match JHU name
  - l0 fixed "-"
  - l1 added gov source for jersey island
  - fix indentation
  - l0 handled cyprus
  - l0 added 8 countries
  - l0 changed Northern Macedonia to match dataset
- 2020-04-24
  - l3 fix so that countries with no reporting on daily testing have nas in daily test/million
  - l3 fixed small mistake making total zero equal to na
  - l3 moved lines dealing with cumratio>100 to affect latest as well
- 2020-04-23
  - l3 fix for daily ratio to allow zeros, and for cumulative ratios disallow values >100
- 2020-04-22
  - l3 added conditions dealing with negative ratios and >100 ratios
  - l3 added condition to replace negative ratios with na
  - l3 added conditions to drop negative test/millions and inf ratios
  - l3 added 2 columns to historical (daily ratio and daily tests/million)
- 2020-04-21
  - l0 added isle of man



Version 0.4 (2020-04-21)

- bug, l1: owid had some dupes in india and usa (2 sources for each)
- feat, l1: add owid/freeze to avoid losing poitns that owid drop
- feat, l0: add portugal from owid dropped data
- feat, l0: added 11 countries by students and 4 coutries by HT. Post processed morocco and dominican republic


Version 0.3 (2020-04-20)

- enh, l3: save historical containing ratio positives and tests/mill in separate file
- enh, l1: rename some countries for consistency across sources: US-DC, US-virgin islands, South Korea
- bugfix, l0: for armenia: turns out that the column name called "negative" is actually "total_cumul", so no need for postprocessing anymore
- feat, l1: give our biominers notion tables higher priority than wikipedia
- enh, l0 argentina: use negative+confirmed only for entries in notion where we dont already have total_cumul
- feat, l3: convert from R to py


Version 0.2 (2020-04-16)

- enh, l2: re-enable yemen, samoa, mariana
- feat, l1: jhu deaths also and merge with confirmed
- enh, l2: use jhu data instead of kaggle
- enh, l1: get jhu confirmed cases
- enh, l2: some more details for null lats
- enh, l2: count file now accumulates results
- enh, l1: drop some spain outliers from wiki and worldometers and owid/ortiz
- bug, l2: new york inconsistency between confirmed cases and total tests on march 12
- feat, l1: add covidtracking.com source
- enh, l0,l1,l2: use subdirectories + owid/roser simplified columns to subset
- enh, l0: lebanon add airport and non-airport
- enh, l0: cast total tests to int
- bug, l1: skip kaggle germany outlier in confirmed cases
- bug, l1: fix florida jump of 100k confirmed cases from apr 12 to apr 13
  - as of 2020-04-15, kaggle fixed this
- feat, l0: add new tables in notion maintained by halim
- enh, l2: moved minor over-writing of data up in pipeline and added assertions to avoid over-writing if data changes value/source
- feat: drop daily owid/roser source and get cumulative one and integrate. This is a major source of data


Version 0.1 (2020-04-14)

- feat: l2: add to latest more fields such as latest totals date, first totals date, count totals, latest confirmed date
- feat: l2: add conversion from historical to latest
- bugfix: l0: bosnia re-compute total from neg+pos
- feat: first working version of commands l0, l1, l2 (implemented in python)
  - l3 still in R ATM

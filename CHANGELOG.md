All entries in reverse chronological order.


Version 0.3 (?)

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

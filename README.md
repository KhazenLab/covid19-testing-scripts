# covid19-testing-scripts

Scripts that process data from/into the git repo `covid19-testing-data`

## Description

- `l0_importBiominers.py`
- `l1_importOthers.py`
- `l2_mergeTogether.R` (better replace this with a python script)
- `l3_postprocessRCsv.sh`

## Install

For the python scripts

```
pip3 install pew
pew new biominers_covid19
pip3 install notion pandas Click
```

For the R scripts

```
install.packages(c("data.table", "zoo"))# , "caret", "hexbin"))
```

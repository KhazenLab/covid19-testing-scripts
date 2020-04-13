# covid19-testing-scripts

Scripts that process data from/into the git repo `covid19-testing-data`


## Description

This is a description of what each command does.

Check usage section below for the exact command syntax.

List of functional commands:

- `l0_importBiominers`: import notion tables
- `l1_importOthers`: import ourworldindata.org and wikipedia and worldometers and merge with biominers

WIP commands

- `l2_mergeTogether`: merge with confirmed cases
- `l4_interpolate.R`: interpolate and extrapolate


## Installation

```
pip3 install pew
pew new biominers_covid19
pip3 install notion pandas Click
```

## Usage

```
python3 main.py l0-importbiominers \
    ~/Development/bitbucket.org/shadiakiki1986/shadi-configs/notion-shadiakiki1986-token_v2.txt \
    ~/Development/gitlab.com/biominers/covid19-testing/multiple-biominers-gitrepo.csv 

python3 main.py l1-importothers \
  ~/Development/gitlab.com/biominers/covid19-testing/

# WIP
python3 main.py l2-mergeTogether \
  ~/Development/gitlab.com/biominers/covid19-testing/
```

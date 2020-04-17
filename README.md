# covid19-testing-scripts

Scripts that process data from/into the git repo `covid19-testing-data`



## Installation

```
pip3 install pew
pew new biominers_covid19
pip3 install notion pandas Click
```

It also helps to see CSVs in the terminal with vd:

```
pip3 install visidata
```

## Usage

Step 0: import notion tables

- This requires the notion token, as documented at https://github.com/jamalex/notion-py/
- The exact documentation from that page of how to get this is:

    Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so"


Command to run step 0:

```
python3 main.py l0-importbiominers \
    path/to/notion/key.txt \
    ~/Development/gitlab.com/biominers/covid19-testing-data/l0-notion_tables/multiple-biominers-gitrepo.csv 
```


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

Deprecated in favor of the new python command:

- `l3_interpolateAndExtend.R`
- `l3_interpolateAndExtend_v2.R`

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
pip3 install vd
```

## Usage

Step 0: import notion tables

```
python3 main.py l0-importbiominers \
    ~/Development/bitbucket.org/shadiakiki1986/shadi-configs/notion-shadiakiki1986-token_v2.txt \
    ~/Development/gitlab.com/biominers/covid19-testing-data/l0-notion_tables/multiple-biominers-gitrepo.csv 
```

Step 1: import non-biominer tables and merge with biominer

(This includes ourworldindata.org, wikipedia, and worldometers)

```
python3 main.py l1-importothers \
  ~/Development/gitlab.com/biominers/covid19-testing-data/
```

Step 2a: get confirmed cases data from kaggle

```
# Install kaggle CLI
# pip3 install --user --upgrade kaggle==1.5.6 2>&1
pip3 install --user --upgrade kaggle 2>&1
pip3 show kaggle

# configure kaggle key
mkdir -p ~/.kaggle/
cp path/to/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

echo 'kaggle version'
kaggle --version 2>&1

# download
rm -rf /tmp/train.csv
kaggle competitions download -c covid19-global-forecasting-week-4 -f train.csv -p /tmp
mv /tmp/train.csv ~/Development/gitlab.com/biominers/covid19-testing-data/l1a-non-biominer_data/kaggle-confirmed.csv
```

Step 2b: merge with confirmed cases

(TODO add extracting the latestOnly file as well)

```
python3 main.py l2-mergetogether \
  ~/Development/gitlab.com/biominers/covid19-testing-data/
```

Step 3: interpolate and extrapolate (R code run by Halim)

```
Rscript l3_interpolateAndExtend.R
```

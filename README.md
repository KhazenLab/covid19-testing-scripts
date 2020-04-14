# covid19-testing-scripts

Scripts that process data from/into the git repo `covid19-testing-data`



## Installation

```
pip3 install pew
pew new biominers_covid19
pip3 install notion pandas Click
```

## Usage

Step 1: import notion tables

```
python3 main.py l0-importbiominers \
    ~/Development/bitbucket.org/shadiakiki1986/shadi-configs/notion-shadiakiki1986-token_v2.txt \
    ~/Development/gitlab.com/biominers/covid19-testing/multiple-biominers-gitrepo.csv 
```

Step 2: import non-biominer tables and merge with biominer

(This includes ourworldindata.org, wikipedia, and worldometers)

```
python3 main.py l1-importothers \
  ~/Development/gitlab.com/biominers/covid19-testing/
```

Step 3a: get confirmed cases data from kaggle

```
ls /content/kaggle.json
pip3 install --user --upgrade kaggle==1.5.6 2>&1
echo 'pip show kaggle'
pip3 show kaggle
mkdir -p /root/.kaggle/
cp /content/kaggle.json /root/.kaggle/
chmod 600 /root/.kaggle/kaggle.json
# kbin=/root/.local/bin/kaggle
kbin=/usr/local/bin/kaggle
echo 'kaggle version'
$kbin --version 2>&1
echo 'kaggle download'
rm train.csv test.csv submission.csv
$kbin competitions download -c covid19-global-forecasting-week-4 2>&1
rm test.csv submission.csv
mv train.csv ~/Development/gitlab.com/biominers/covid19-testing/kaggle-confirmed.csv
```

Step 3b: merge with confirmed cases

(TODO add extracting the latestOnly file as well)

```
# WIP
python3 main.py l2-mergetogether \
  ~/Development/gitlab.com/biominers/covid19-testing/
```

Step 4: interpolate and extrapolate

```
Rscript l4_interpolate.R
```

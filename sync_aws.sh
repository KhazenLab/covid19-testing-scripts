#!/bin/sh

# --acl option is to make the folder public
# If the `--acl` doesn't work (it works as of 2020-05-12), then make the folder public manually in aws web console.
# (https://github.com/aws/aws-cli/issues/1560)


# sync everything
#AWS_PROFILE=shadi_shadi aws s3 sync www/ s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read

## High prio
AWS_PROFILE=shadi_shadi aws s3 cp www/index.html s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
AWS_PROFILE=shadi_shadi aws s3 cp www/t11d-chisquared_dashboard-simple.html s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
AWS_PROFILE=shadi_shadi aws s3 cp www/t11d-layout.css s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
AWS_PROFILE=shadi_shadi aws s3 cp www/t11c-country_latest_table.html s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
AWS_PROFILE=shadi_shadi aws s3 cp www/t12b-plotSourcesOverTime-stacked.png s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read

## Low priority
#AWS_PROFILE=shadi_shadi aws s3 cp www/p5_global_scatter.html s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
AWS_PROFILE=shadi_shadi aws s3 cp www/t11d-chisquared_dashboard-detailed.html s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
#AWS_PROFILE=shadi_shadi aws s3 cp www/t12b-plotSourcesOverTime-lines.png s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read
AWS_PROFILE=shadi_shadi aws s3 cp www/t16a-postprocessing_dashboard.html s3://biominers-b1/covid19-testing-data/ --acl bucket-owner-full-control --acl public-read


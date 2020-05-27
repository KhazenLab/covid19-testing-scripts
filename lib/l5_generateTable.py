from os.path import join
import pandas as pd
import numpy as np
import pandas as pd
import numpy as np
from bokeh.io import show, output_notebook
from bokeh.plotting import  ColumnDataSource, output_file
from bokeh.models.widgets import  DataTable, NumberFormatter, TableColumn,Div
from bokeh.layouts import column

class L5GenerateTable:
    """
    Class that reads csv file from ARCGIS/v2 and generates table for l5table
    """
    def read_csv(self, dir_gitrepo):
        csv_arc_latest = join(dir_gitrepo, "ArcGIS/v2", "t11c-confirmedtotalTests-latestOnly.csv")
        df_latest = pd.read_csv(csv_arc_latest)
        df_latest=df_latest.drop(['Lat', 'Long','Updated'], axis=1)
        df_latest=df_latest.rename(columns={"CountryProv": "Country/State", 
                                    "Max - ConfirmedCases":"Cumulative ConfirmedCases",
                                    "Max - Fatalities":"Cumulative Fatalities",
                                    "Max - total_cumul.all":"Cumulative Total Tests",
                                    "Max - Population":"Population",
                                    "Max - tests_per_mil":"Cumulative Tests per Million",
                                    'Max - ratio_confirmed_total_pct':'Cumulative Confirmed/Tests (%)',
                                    'Max - negative_cases':'Cumulative Negative Cases'})
        self.df_latest=df_latest
    def to_html(self, dir_plot_destination):
        fn_dest = join(dir_plot_destination, "t11c-country_latest_table.html")
        output_file(fn_dest)
        self.df_latest=self.df_latest.fillna(-1)
        source = ColumnDataSource(self.df_latest)
        columns = [
        TableColumn(field="Country/State", title="Country/State"),
        TableColumn(field="Cumulative ConfirmedCases", title="Cumulative ConfirmedCases",formatter=NumberFormatter()),
        TableColumn(field="Cumulative Fatalities", title="Cumulative Fatalities",formatter=NumberFormatter()),
        TableColumn(field="Cumulative Total Tests", title="Cumulative Total Tests",formatter=NumberFormatter()),
        TableColumn(field="Cumulative Negative Cases", title="Cumulative Negative Cases",formatter=NumberFormatter()),
        TableColumn(field="Cumulative Tests per Million", title="Cumulative Tests per Million",formatter=NumberFormatter()),
        TableColumn(field="Cumulative Confirmed/Tests (%)", title="Cumulative Confirmed/Tests (%)",formatter=NumberFormatter()),
        TableColumn(field="Population", title="Population",formatter=NumberFormatter())
        ]
        data_table = DataTable(source=source, columns=columns,sizing_mode="stretch_both",index_position=None)
        show(column([data_table,Div(text="Cells with -1 represent missing values",style={'color':'whitesmoke'})],sizing_mode="stretch_width",background='rgb(70,70,70)'))
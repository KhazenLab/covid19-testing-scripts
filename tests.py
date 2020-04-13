from .lib import get_table, postprocess_table


# test
# get_table("Armenia").head()
# get_table("Estonia").head()
get_table("Colombia").head()



# test
#country_name = "Argentina"
#country_name = "Armenia"
#country_name = "Austria"
#country_name = "Bahrain"
#country_name = "Bangladesh"
#country_name = "Bolivia"
#country_name = "Bosnia"
#country_name = "Colombia"
#country_name = "Costa Rica"
country_name = "Croatia"
#country_name = "Estonia"
#country_name = "Japan"
#country_name = "Jordan"
#country_name = "Lebanon"
#country_name = "Philippines"
postprocess_table(country_name, get_table(country_name))[["Date","total_cumul"]]



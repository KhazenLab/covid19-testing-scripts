#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

disableAll<-function()
{
    shinyjs::disable("country_select")
    shinyjs::disable("data_select")
    shinyjs::disable("plot_select")
    shinyjs::disable("date_select")
    
}
enableAll<-function()
{
    shinyjs::enable("country_select")
    shinyjs::enable("data_select")
    shinyjs::enable("plot_select")
    shinyjs::enable("date_select")
    
}

library(shinyWidgets)
library(shiny)
library(shinycssloaders)
library(plotly)
library(shinythemes)
library(shinyjs)
library(data.table)
mycss <- "
body{
background-color:rgb(70,70,70)
}

#sidebar{
margin-top:0px;
margin-left:-10px;

margin-right:0px;
background-color:rgb(70,70,70);
border-color:rgb(70,70,70);
max-width:300px;
}
#mainbar{
margin-top:50px;
margin-left:-50px;
border-width:1px;
border-color:black;
}
.js-irs-0 .irs-single, .js-irs-0 .irs-bar-edge, .js-irs-0 .irs-bar {
                                                  background: rgb(50,50,50);
                                                  border-top: 1px solid rgb(50,50,50) ;
                                                  border-bottom: 1px solid rgb(50,50,50) ;}

                            /* changes the colour of the number tags */
                           .irs-from, .irs-to, .irs-single { background:rgb(50,50,50) ;
                                                             color: white}


.selectize-dropdown {
background-color:rgb(50,50,50) !important;
color: white !important;
caret-color: white !important;
}

.selectize-input{
background-color:rgb(50,50,50) !important;
color: white !important;

caret-color: white !important;
}

.selectize-input:after {
border-color:#ffffff transparent transparent transparent !important;


}
"

# Define UI for application that draws a histogram
ui <- fluidPage(theme = shinytheme("slate"),
    tags$style(mycss),
    useShinyjs(),

    # Sidebar with a slider input for number of bins 
    sidebarLayout( 
    sidebarPanel(id="sidebar",
        selectizeInput(
                'country_select', label=HTML("Countries (maximum 10)") ,choices = NULL,
                options = list(maxItems=10,'plugins' = list('remove_button'),
                               'create' = TRUE,
                               'persist' = FALSE)
                ),

        selectInput(
                'data_select', HTML("Measurment Type"),choices = NULL
                    
            ),
        selectInput(
          'plot_select', HTML("Plot Type"),choices = NULL
          
        ), 
        sliderTextInput("date_select",HTML("<br>Date Range"),choices=c(0,1),selected=c(0,1)),
        uiOutput("textOutput"),width = 3
            
    ),
    
        # Show a plot of the generated distribution
       
    mainPanel( id="mainbar",       
    div(id="plotdiv",withSpinner(plotlyOutput("distPlot")))
    
    )
    )
    
)

# Define server logic required to draw a histogram
server <- function(input, output,session) {
    disableAll();
    dataList<-list("Daily Total Tests","Daily Positive Tests","Daily Negative Tests","Cumulative Total Tests","Cumulative Positive Tests","Cumulative Negativs Tests", "Daily Positives/Tests (%)",
                   "Cumulative Positives/Tests (%)","Daily Tests/Million","Cumulative Tests/Million","Daily Tests/Positives","Cumulative Tests/Positives")
    updateSelectInput(session, 'data_select', choices=dataList,selected=dataList[7])
    plotList<-list("Linear Plot","Bar Plot")
    updateSelectInput(session, 'plot_select', choices=plotList,selected=plotList[1])
    colors<-c("#ed5151","#149ece","#a7c636","#9e559c","#fc921f","#ffde3e","#b7814a","#3caf99","#e0f6a7","#7570b3")
    
    df_historical=read.csv("https://halimt.maps.arcgis.com/sharing/rest/content/items/8f6a34ab1f8342fe961f94090cfef757/data")
    df_historical2=read.csv("https://halimt.maps.arcgis.com/sharing/rest/content/items/8516ac8dfdf24d3c89e972f3a55e4c1b/data")
    
    df_historical$CountryProv <- (gsub("-+",'-',iconv(df_historical$CountryProv, "UTF-8", "ASCII", sub = "-")))
    df_historical2$CountryProv <- (gsub("-+",'-',iconv(df_historical2$CountryProv, "UTF-8", "ASCII", sub = "-")))
    
    df=data.frame("CountryProv"=df_historical["CountryProv"],
                  "Date"=df_historical["Date"],
                    "DailyTotal"=df_historical2[df_historical2["Positive.Negative"]=="Positive","dailyValue"]+df_historical2[df_historical2["Positive.Negative"]=="Negative","dailyValue"],
                    "DailyPositive"=df_historical2[df_historical2["Positive.Negative"]=="Positive","dailyValue"],
                    "DailyNegative"=df_historical2[df_historical2["Positive.Negative"]=="Negative","dailyValue"],
                    "CumTotal"=df_historical2[df_historical2["Positive.Negative"]=="Positive","cumulativeValue"]+df_historical2[df_historical2["Positive.Negative"]=="Negative","cumulativeValue"],
                    "CumPositive"=df_historical2[df_historical2["Positive.Negative"]=="Positive","cumulativeValue"],
                    "CumNegative"=df_historical2[df_historical2["Positive.Negative"]=="Negative","cumulativeValue"],
                    "DailyRatio"=df_historical["daily_ratio_confirmed_total_pct"],
                    "CumRatio"=df_historical["ratio_confirmed_total_pct"],
                    "DailytestsMill"=df_historical["daily_tests_per_mil"],
                    "CumtestsMill"=df_historical["tests_per_mil"],
                    "DailyTestsperPositive"=df_historical["daily_tests_per_positive"],
                    "CumTestsperPositive"=df_historical["tests_per_positive"])
    
    
    listCountries<-c('US -','Canada -','Australia -');
    countryNames<-c('United States','Canada','Australia')
    populations<-c(330637037,37678383,25443205)
    for(i in 1:length(listCountries))
    {
      dfUS<-(aggregate(.~Date,data=df[df$CountryProv %like% listCountries[i],c(2:ncol(df))],FUN=sum,na.action = na.pass))
      dfUS$ratio_confirmed_total_pct=dfUS$CumPositive*100/dfUS$CumTotal;
      
      dfUS$ratio_confirmed_total_pct[dfUS$ratio_confirmed_total_pct>=100]=NA
      
      dfUS$daily_ratio_confirmed_total_pct=dfUS$DailyPositive*100/dfUS$DailyTotal;
      dfUS$daily_ratio_confirmed_total_pct[dfUS$daily_ratio_confirmed_total_pct>=100]=NA
      dfUS$daily_ratio_confirmed_total_pct[dfUS$daily_ratio_confirmed_total_pct<0]=NA
      dfUS$daily_ratio_confirmed_total_pct=round(dfUS$daily_ratio_confirmed_total_pct,2)
      
      dfUS$ratio_confirmed_total_pct=round(dfUS$ratio_confirmed_total_pct,2)
      
      dfUS$tests_per_mil=floor(dfUS$CumTotal*1000000/populations[i]);
      dfUS$daily_tests_per_mil=floor(dfUS$DailyTotal*1000000/populations[i]);
      dfUS$daily_tests_per_mil[dfUS$daily_tests_per_mil<0]=NA
      dfUS$CountryProv=countryNames[i]
      dfUS["DailyTestsperPositive"]=round(dfUS["DailyTotal"]/dfUS["DailyPositive"],2);
      dfUS["CumTestsperPositive"]=round(dfUS["CumTotal"]/dfUS["CumPositive"],2);
      
      dfUS=dfUS[, names(df)]
      df<-rbind(df,dfUS)
      
    }
    df <- df[order(df$CountryProv),]
    
    listInitial<-c("Australia","United States","United Kingdom","Italy","Argentina","Iceland","Lebanon","South Korea")
    listInitial<-sort(listInitial)
    updateSelectizeInput(session, 'country_select', choices = unique(df$CountryProv), selected=listInitial,server = TRUE)
    
    f1<- list(
        size = 18,
        color = "white"
    )
    f2 <- list(
        size = 14,
        color = "white"
    )
    a <- list(
        title="Date",
        titlefont = f1,
        tickfont = f2,
        
        linecolor = ("gray"),
        showgrid = T,
        gridcolor=('gray'),
        mirror=T,
        ticks='outside',
        showline=T
    )
    b <- a
    a$nticks=10;
    a$tickangle=-45;
    
    minDate=min(as.Date(as.character(df[,"Date"]),format="%Y-%m-%d"))
    maxDate=max(as.Date(as.character(df[,"Date"]),format="%Y-%m-%d"))
    
    
    choice=seq(as.Date(minDate), as.Date(maxDate), by="days");
    updateSliderTextInput(session,inputId = "date_select",
                          label = "Date Range",
                          choices=choice,
                          selected=c(choice[1],choice[length(choice)]))
    
    
    
    
    
    
    enableAll();
    
    P <- plot_ly()
    observeEvent({input$country_select
        input$data_select
        input$plot_select
        input$date_select},
                 {
                   
                     b$title=input$data_select
                     if(nrow(df[df$CountryProv==input$country_select,])<=0)
                             return();
                          dfDates=(as.Date(as.character(df[,"Date"]),format="%Y-%m-%d"))
                          df1=df[dfDates>=as.Date(as.character(input$date_select[1]),format="%Y-%m-%d") & dfDates<=as.Date(as.character(input$date_select[2]),format="%Y-%m-%d"),]
                         
                         output$distPlot<-renderPlotly({
                             P$data=NULL;
                             for(i in 1:length(input$country_select))
                             {
                             
                             yAxis<-df1[df1$CountryProv==input$country_select[i],match(input$data_select,dataList)+2];
                             xAxis<-df1[df1$CountryProv==input$country_select[i],"Date"];
                             #yAxis[is.na(yAxis)] <- 0;
                             
                             dfk<-data.frame(xAxis,yAxis)
                             
                             if(input$plot_select=="Bar Plot")
                             {
                               P <-add_trace(P,data=dfk,x = ~xAxis, y = yAxis,  
                                             type="bar",marker = list(color = colors[i]), name=input$country_select[i]) 
                               
                             }
                             else
                             {
                               P <-add_trace(P,data=dfk,x = ~xAxis, y = yAxis,  
                                             type="scatter", mode="lines+markers", line = list(color = colors[i]),marker = list(color = colors[i]),name=input$country_select[i]) 
                               
                             }
                             
                              }
                         if(input$plot_select=="Bar Plot")
                         {
                             P%>%
                                 layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor = "rgba(0, 0, 0, 0)"
                                        ,coloraxis="rgb(255,255,255)",xaxis=a,yaxis=b,barmode="stack",legend = list(traceorder='normal',font=f2))
                         }
                         else
                         {
                           P%>%
                             layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor = "rgba(0, 0, 0, 0)"
                                    ,coloraxis="rgb(255,255,255)",xaxis=a,yaxis=b,legend = list(font=f2))
                           
                         }
                             
                     })
                 })
    output$textOutput<-renderUI({
      req(input$data_select)
      if(input$data_select=="Daily Tests/Positives")
      HTML("<br>Note that Daily Tests/Positives could have missing data points when the daily positive number is zero")
    
      
    })
    
   
}

# Run the application 
shinyApp(ui = ui, server = server)

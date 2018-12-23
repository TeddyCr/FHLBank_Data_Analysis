#!/usr/bin/env python3

from helpers import sendRequest, getDownloadURLs, downloadFiles, aggregateFiles
import os
import traceback
import pandas as pd
import plotly
import plotly.graph_objs as go

def initializeFiles():
    """
    Initialize the files to be analyzed in the input folder. This function
    will scrape the fhfa website to get the available loan data information
    """

    # Prepare data for request
    domain = 'https://www.fhfa.gov' 
    extension = '/DataTools/Downloads/Pages/FHLBank-Public-Use-Database-Previous-Years.aspx'
    url = domain + extension

    # Check if folders exist, otherwise create them
    if not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__))
                                       ,'data','input')):
        os.makedirs('data/input')
    if not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__))
                          ,'data','output')):
        os.makedirs('data/output')

    response = sendRequest(url)
    download_urls = getDownloadURLs(response)

    downloadFiles(domain, download_urls)

    aggregateFiles(os.path.join(os.path.dirname(os.path.dirname(__file__)),'data'))

    return True 

def getFile():
    path_to_output = os.path.join(os.path.dirname(os.path.dirname(__file__))
                                  ,'data', 'output')
    for dircs, subdircs, files in os.walk(path_to_output):
        for file in files:
            if '.csv' in file:
                df = pd.read_csv(os.path.join(path_to_output,file),low_memory=False)
                df = df[df['First'] == 1]

    return df


def firstTimeBorrowerAge(df=pd.DataFrame()):
    if df.empty:
        df = getFile()

    df = df[['Year','BoAge']].groupby('Year', as_index=False).mean()
    x, y = df['Year'], df['BoAge']
    title = 'Average Age of First Time Home Buyer (2009-2017)'
    xaxis, yaxis = 'Years', 'Avg. Age'

    line = go.Scatter(x=x,y=y, line = dict(color = ('rgb(34, 167, 240)'))
                     , name='Average Age')
    data = [line]

    drawLineGraphs(data,title, xaxis, yaxis)


def firstTimeBorrowerGender(df=pd.DataFrame()):
    if df.empty:
        df = getFile()

    df = df.groupby(['Year','BoGender'])['BoGender'].agg({'BoGender': 'count'})
    df['percentage'] = df.groupby(level=0).apply(lambda x: x / x.sum() * 100)

    x_m, y_m = df.index.levels[0], df[df.index.get_level_values('BoGender')==1].percentage 
    x_f, y_f = df.index.levels[0], df[df.index.get_level_values('BoGender')==2].percentage 

    line_m = go.Scatter(x=x_m,y=y_m,line = dict(color = ('rgb(34, 167, 240)')), name='Male')
    line_f = go.Scatter(x=x_f,y=y_f, line = dict(color = ('rgb(248,23,23)')),name='Female')

    data = [line_m, line_f]

    title = 'First Time Home Buyer By Gender (2009-2017)'
    xaxis, yaxis = 'Years', 'Percentage of Borrower By Gender'

    drawLineGraphs(data,title, xaxis, yaxis)


def firstTimeBorrowerIncome(df=pd.DataFrame()):
    if df.empty:
        df = getFile()

    df_inc = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__))
                                      ,'data','input','census','income_data.csv'))
    
    df = df[['Year', 'Income']].groupby('Year', as_index=False).mean()
    df['pct_change'] = df.pct_change().Income
    x, y1 = df['Year'], df['Income']
    y2 = df['pct_change']
    x2, y3 = df_inc['year'], df_inc['income']
    line1 = go.Scatter(x=x,y=y1,line = dict(color = ('rgb(34, 167, 240)'))
                       ,mode = 'lines+markers', name='Avg. Ann. Income (in $)')
    line2 = go.Scatter(x=x,y=y2,line = dict(color = ('rgb(34, 167, 240)')
                       , dash = 'dot'), name='Income Growth (in %)', yaxis='y2')
    line3 = go.Scatter(x=x2, y=y3,line = dict(color = ('rgb(248,23,23)'))
                       , mode = 'lines+markers', name='Median National Income')

    data = [line1,line2, line3]

    title = 'Avg. Borrower Annual Income in $ by Year'
    xaxis = 'Years'
    yaxis = 'Avg. Income in $'

    drawLineGraphs(data, title,xaxis,yaxis, dual=True)


def firstTimeBorrowerEthnicity(df=pd.DataFrame()):
    if df.empty:
        df = getFile()

    df_eth = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__))
                        ,'data/input/census/demographic_data.csv'))
    df_eth = df_eth.set_index('year')
    df_eth = df_eth.div(df_eth.sum(axis=1), axis=0) * 100
    
    x1, y01 = list(df_eth.index), df_eth['White']
    y02 = df_eth['Black or African American']
    y03 = df_eth['American Indian and Alaska Native']
    y04 = df_eth['Asian']
    y05 = df_eth['Native Hawaiian and Other Pacific Islander']

    df = df.groupby(['Year', 'BoRace'])['BoRace'].agg({'BoRace':'count'})
    df['percentage'] = df.groupby(level=0).apply(lambda x: x/x.sum() * 100)

    x, y1 = df.index.levels[0], df[df.index.get_level_values('BoRace')==1].percentage
    y2 = df[df.index.get_level_values('BoRace')==2].percentage
    y3 = df[df.index.get_level_values('BoRace')==3].percentage
    y4 = df[df.index.get_level_values('BoRace')==4].percentage
    y5 = df[df.index.get_level_values('BoRace')==5].percentage

    line1 = go.Scatter(x=x,y=y1,line = dict(color = ('rgb(255, 211, 42)'))
                      ,mode = 'lines+markers', name='Am. Indian or AK Nat.')
    line2 = go.Scatter(x=x,y=y2,line = dict(color = ('rgb(15, 188, 249)'))
                      ,mode = 'lines+markers', name='Asian')
    line3 = go.Scatter(x=x,y=y3,line = dict(color = ('rgb(5, 196, 107)'))
                      ,mode = 'lines+markers', name='Black or Af.Am.')
    line4 = go.Scatter(x=x,y=y4,line = dict(color = ('rgb(245, 59, 87)'))
                      ,mode = 'lines+markers', name='Native HI or Other Pac. Isl.')
    line5 = go.Scatter(x=x,y=y5,line = dict(color = ('rgb(128, 142, 155)'))
                      ,mode = 'lines+markers', name='White')

    line01 = go.Scatter(x=x1,y=y03,line = dict(color = ('rgb(255, 211, 42)')
                       , dash = 'dot'),mode = 'lines+markers', name='Census, Am. Ind. or AK Nat.')
    line02 = go.Scatter(x=x1,y=y04,line = dict(color = ('rgb(15, 188, 249)')
                       , dash = 'dot'),mode = 'lines+markers', name='Census, Asian')
    line03 = go.Scatter(x=x1,y=y02,line = dict(color = ('rgb(5, 196, 107)')
                       , dash = 'dot'),mode = 'lines+markers', name='Census, Black or Af.Am.')
    line04 = go.Scatter(x=x1,y=y05,line = dict(color = ('rgb(245, 59, 87)')
                       , dash = 'dot'),mode = 'lines+markers', name='Census, Native HI or Other Pac. Isl.')
    line05 = go.Scatter(x=x1,y=y01,line = dict(color = ('rgb(128, 142, 155)')
                       , dash = 'dot'), mode = 'lines+markers',name='Census, White')

    data = [line1, line2, line3, line4, line5,line01, line02, line03, line04, line05]

    title = 'First Time Home Buyer By Ethnic Group (2009-2017)'
    xaxis, yaxis = 'Years', 'Percentage of Borrower By Ethnicity'

    drawLineGraphs(data, title, xaxis, yaxis)


def drawLineGraphs(data, title, xaxis, yaxis, dual=False):
    plotly.tools.set_credentials_file(username=os.environ.get('USER')
                                      , api_key=os.environ.get('api_key'))
    if dual:
        layout = dict(title=title, xaxis={'title':xaxis}, yaxis={'title':yaxis}
                     , yaxis2={'side':'right','overlaying':'y'})
    else:    
        layout = dict(title=title, xaxis={'title':xaxis}, yaxis={'title':yaxis})

    data = data
    fig = dict(data=data, layout=layout)
    plotly.plotly.plot(fig)


def executeFlow():
    path_to_output = os.path.join(os.path.dirname(os.path.dirname(__file__))
                                  ,'data', 'output')
    for dircs, subdircs, files in os.walk(path_to_output):
        for file in files:
            if not os.path.isfile(os.path.join(path_to_output,file)): 
                initializeFiles()
            
            df = getFile()

            print(df.info(verbose=True,null_counts=True))

            firstTimeBorrowerAge(df=df)
            firstTimeBorrowerGender(df=df)
            firstTimeBorrowerIncome(df=df)
            firstTimeBorrowerEthnicity(df=df)

executeFlow()
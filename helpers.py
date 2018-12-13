#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
from urllib import request
import os
import csv

def sendRequest(url):
    url = url
    headers = {'user-agent':'Teddy Crepineau (teddy.crepineau@gmail.com)'}
    response = requests.get(url, headers=headers)
    return response.text

def getDownloadURLs(HTTPResponse):
    soup = BeautifulSoup(HTTPResponse, 'lxml')
    tds = soup.find_all(class_='ms-rteTableOddCol-4')
    download_urls = []
    for td in tds:
        download_urls.append(td.a['href'])

    return download_urls

def downloadFiles(domain, download_urls):
    for download_url in download_urls:
        search_name = re.search(r'/(\w+.csv)',download_url)
        file_name = search_name.group(1)
        path = os.path.join(os.path.dirname(__file__),'data','input',file_name)
        
        url = domain + download_url
        
        fdata =  request.urlopen(url)
        
        with open(path, 'wb') as f:
            f.write(fdata.read())

def aggregateFiles(path):
    fieldnames = []
    in_path = os.path.join(path, 'input')
    out_path = os.path.join(path,'output','FHL_Aggregated_Data.csv')

    for dircs, subdirc, files in os.walk(in_path):
        for file in files:
            with open(os.path.join(in_path,file), 'r',newline='') as f:
                reader = csv.reader(f)
                headers = next(reader)
                for header in headers:
                    if header not in fieldnames:
                        fieldnames.append(header)

    with open(out_path, 'w', newline='') as f_output:
        writer = csv.DictWriter(f_output, fieldnames=fieldnames)
        writer.writeheader()
        for dircs, subdirc, files in os.walk(in_path):
            for file in files:
                with open(os.path.join(in_path,file), 'r',newline='') as f_input:
                    reader = csv.DictReader(f_input)
                    for line in reader:
                        writer.writerow(line)

    return True
#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
from urllib import request
import os
import csv
import json


# File Fetching + Aggregation Functions
# -------------------------------------
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
        path = os.path.join(os.path.dirname(os.path.dirname(__file__))
                            ,'data','input',file_name)
        
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


# Medium Publlication Functions 
# -----------------------------

KEY = os.environ.get('MEDIUM_KEY')

def fetchPosts(url=None):
    if not url:
        url = "https://medium.com/feed/@teddycrpineau"

    get_posts = requests.get(url)
    get_posts_xml = get_posts.text
    soup = BeautifulSoup(get_posts_xml, 'html.parser')
    xml_titles = soup.find_all('title')

    titles = set()

    for title in xml_titles:
        titles.add(title.contents[0])
    
    return titles


def hasBeenPublished(fetched_posts=None):
    base_dirc = os.path.dirname(os.path.dirname(__file__))
    dirc = 'blog_posts'
    path = os.path.join(base_dirc,dirc)

    files_status = dict()

    for dirs, subdirs, files in os.walk(path):
        for file in sorted(files[:4], key=lambda file: os.path.getmtime(os.path.join(path
                          ,file)), reverse=True):  # Sort files by most recently modified
            if file.replace('_', ' ') not in fetched_posts:
                files_status[os.path.join(path,file)] = True
            else:
                files_status[os.path.join(path,file)] = False

    return files_status

def getMediumProfileInfo():
    request_url = 'https://api.medium.com/v1/me'

    headers = {'Authorization': f'Bearer {KEY}'
              ,'Content-Type': 'application/json'}

    profile_info = requests.get(request_url, headers=headers)
    json_profile_info = json.loads(profile_info.text)
    profile_id = json_profile_info['data']['id']

    return profile_id


def pushPostToMedium(post=None,publishStatus='draft', contentFormat='html'):
    if not post:
        raise Exception("Path to the post must be specified")

    content = str()
    tags = list()
    with open(post, 'r') as f:
        for line in f.readlines():
            if 'TAGS' in line:
                tmp = re.split(r'\W+', line)
                for tag in tmp[1:]:
                    if tag is not '':
                        tags.append(tag) 
            else:
                content += line

    re_search = re.search(r'([\w\-]+)\.', post)
    url_string = re_search.group(1)
    title = url_string.replace('-', ' ')

    profile_id = getMediumProfileInfo()

    request_url = f'https://api.medium.com/v1/users/{profile_id}/posts'

    headers = {'Authorization': f'Bearer {KEY}'
               ,'Content-Type': 'application/json'}

    body = {
            "title": title,
            "contentFormat": contentFormat,
            "content": f"{content}",
            "canonicalUrl": f"http://medium.com/posts/{url_string}",
            "tags": tags,
            "publishStatus": publishStatus
            }

    post_post_request = requests.post(request_url, headers=headers, data=json.dumps(body))
    
    return post_post_request.text
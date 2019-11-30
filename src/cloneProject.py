from pathlib import Path
import pandas as pd
import json
import simplejson
import os

import requests
from requests.auth import HTTPBasicAuth


def getURL(apiURL):
    r = requests.get(apiURL)
    json = r.json()
    return (json['html_url'])

def cloneProject(df):
    for index, rows in df.iterrows():
        os.system("git clone "+getURL(rows['url']))
        #print(df.loc[index].fullURL = getURL(df.loc[index].url))
    
def main():
    PATH_SAMPLE = "/home/thanadon/Documents/Project/Sample_Projects/"
    PATH_CSV = '/home/thanadon/Documents/Project/csv/Visualization_GoodSample.csv' 

    # Create the main directory for cloning projects
    Path(PATH_SAMPLE).mkdir(parents=True, exist_ok=True)
    os.chdir(PATH_SAMPLE)
    os.system("pwd")

    # Read API urls from csv file
    df = pd.read_csv(PATH_CSV)
    #print(df['url'])

    # Get URL of projects
    #getURL(df)

    # Clone projects to local repositories
    cloneProject(df)

main()
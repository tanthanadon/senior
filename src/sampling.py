from github import Github
import mysql.connector
import pandas as pd
from pathlib import Path
import time
import numpy as np
import csv
import seaborn as sns
import matplotlib.pyplot as plt

# importing the requests library
import requests
from pandas.io.json import json_normalize
import json

from tqdm import tqdm, trange, tnrange

# Parsing date
import dateutil.parser

# Multiprocessing
import logging
import multiprocessing as mp
from multiprocessing_logging import install_mp_handler


PATH_CSV = Path("../csv/round_2").resolve()
PATH_CSV.mkdir(parents=True, exist_ok=True)


def query(q):
    conn = mysql.connector.connect(host="localhost", user="benjaporn", passwd="bee", database="ghtorrent")
    return pd.read_sql_query(q, conn)

def getSample():
    q = """SELECT projects.id as project_id, projects.language, projects.url, MAX(project_languages.bytes) as bytes,
            projects.created_at, projects.updated_at, FLOOR((DATEDIFF(projects.updated_at,projects.created_at))/365) as year_diff, 
            projects.forked_from as forked_from
            FROM projects
            INNER JOIN project_languages ON projects.id = project_languages.project_id 
            WHERE project_languages.bytes >= 10000000 
            AND projects.language = "Python"
            AND project_languages.language = "Python"
            AND FLOOR((DATEDIFF(projects.updated_at,projects.created_at))/365) >= 2
            AND (projects.updated_at BETWEEN '2018-05-31 23:59:59' AND '2019-05-31 23:59:59')
            GROUP BY projects.id
            """
        
    df = query(q)
    
    # Clean forked_form status from NaN to 0
    df['forked_from'].replace(np.nan, 0, inplace=True)
    # Convert value in forked_form to be INT
    df['forked_from'] = df['forked_from'].astype(int)
    # Assign original project status from forked_from column by YES or NO
    df['original_project'] = np.where(df['forked_from'] == 0, 'YES', 'NO')

    print(df)
    df.to_csv("{0}/dataSampling_raw.csv".format(PATH_CSV), index=False)

def getAPI(df):
    ls = ["project_id",
            "created_at",
            "updated_at",
            "pushed_at",
            "git_url",
            "ssh_url",
            "clone_url",
            "svn_url",
            "homepage",
            "size",
            "stargazers_count",
            "watchers_count",
            "language",
            "has_issues",
            "has_projects",
            "has_downloads",
            "has_wiki",
            "has_pages",
            "forks_count",
            "mirror_url",
            "archived",
            "disabled",
            "open_issues_count",
            "forks",
            "open_issues",
            "watchers"]
    # print(ls)

    # set up logging to file
    logging.basicConfig(filename='getAPI.log', filemode='w', level=logging.ERROR)

    temp = pd.DataFrame()
    for index, row in tqdm(list(df.iterrows())):
        # print(row)
        # Add URL
        URL = "{0}".format(row.url)

        # sending get request and saving the response as response object 
        headers = {'Authorization': 'token 4fae0c5f5db3a6fe3c24cd9ff7a3581753513b44'}

        r = requests.get(url = URL, headers=headers)

        # Filter result only 200 status will be collected in .csv file
        if(r.status_code==200):
            # Get json from request
            json = r.json()
            # Normalize json to DataFrame
            data = json_normalize(json)
            data['project_id'] = row.project_id

            result = data[ls]
            temp = temp.append(result)
        else:
            logging.error("projectID: {0}, status: {1}".format(row.project_id, r.status_code))
    
    # Rename columns to api_xxx
    temp.rename(columns={"created_at": "api_created_at", "updated_at": "api_updated_at", "pushed_at": "api_pushed_at"}, inplace=True)
    # Reset index
    temp.set_index('project_id', inplace=True)
    temp.reset_index(inplace=True)
    # print(temp)
    result = cleanDate(temp)
    # print(result)

    result.to_csv("{0}/dataSampling_api.csv".format(PATH_CSV), index=False)

def convertDate(date):
    date_format = "%Y-%m-%d %H:%M:%S"
    d = dateutil.parser.parse(date)
    # print(d.strftime(date_format))
    return d.strftime(date_format)

def cleanDate(df):
    for index in df.index:
        df.at[index, 'api_created_at'] = convertDate(df.at[index, 'api_created_at'])
        df.at[index, 'api_updated_at'] = convertDate(df.at[index, 'api_updated_at'])
        df.at[index, 'api_pushed_at'] = convertDate(df.at[index, 'api_pushed_at'])
    # print(df)
    return df

def convertProjectID(arr):
    return ' ,'.join(map(str, arr))

def totalAuthorProject(df):
    # Convert project_id
    # print(len(df['project_id']))
    project_id = convertProjectID(df['project_id'])
    # print(project_id)

    q = """SELECT project_id, COUNT(DISTINCT commits.id) as total_commit FROM commits
            WHERE project_id IN ({0})
            GROUP BY project_id""".format(project_id)
    df = query(q)

    print(df)
    df = df.replace(np.nan, 0)
    df['total_commit'] = df['total_commit'].astype(int)
    df.to_csv("{0}/totalCommit.csv".format(PATH_CSV), index=False)
    return df


start_time = time.time()
if __name__ == "__main__":
    # getSample()
    raw = pd.read_csv("{0}/dataSampling_raw.csv".format(PATH_CSV))

    # Pass filtered samples to calculate total authors
    total_author = totalAuthorProject(raw)

    # getAPI(raw)
    api = pd.read_csv("{0}/dataSampling_api.csv".format(PATH_CSV))

    ################################################################
    df = pd.merge(raw, api, how="inner", on=["project_id", "language"])
    df['compared_date'] = np.where(df['created_at'] == df['api_created_at'], True, False)
    # Filter data by checking created date with data from GitHub API
    df = df[df['compared_date'] == True]
    # Filter data by checking original project status
    df = df[df['original_project'] == 'YES']
    ################################################################


    # Merge cleaned sample and total_author dataframe from GHTorrent
    merged = pd.merge(df, total_author, on='project_id', how='inner')
    
    # Filter data by checking total authors not equal to zero
    merged = merged.loc[merged['total_commit'] != 0]
    # merged = merged.loc[merged['total_commit'] == 0]

    # Final sample projects
    # merged = merged[['project_id', 'url', 'total_commit']]
    print(merged)
    # merged.to_csv("{0}/dataSampling_total_commit_zezro.csv".format(PATH_CSV), index=False)
    merged.to_csv("{0}/dataSampling_final.csv".format(PATH_CSV), index=False)

    # Check projects have zero total commits
    # df = pd.read_csv("/home/senior/senior/csv/round_2/totalCommit.csv")
    # print(df[df['total_commit'] == 0])

print("--- %s seconds ---" % (time.time() - start_time))

    
    
import mysql.connector
import pandas as pd
from pathlib import Path
import time
import numpy as np
import csv
import seaborn as sns
import matplotlib.pyplot as plt

import requests
from bs4 import BeautifulSoup

from datetime import datetime

PATH_CSV = Path("../csv/round_2").resolve()

def convertProjectID(arr):
    return ' ,'.join(map(str, arr))

def query(q):
    conn = mysql.connector.connect(host="localhost", user="benjaporn", passwd="bee", database="ghtorrent")
    return pd.read_sql_query(q, conn)

def getIQR(df):
    q1, q3 = np.percentile(df, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 -(1.5 * iqr) 
    upper_bound = q3 +(1.5 * iqr)
    return lower_bound, upper_bound

def detect_outlier(df):
    df = df.sort_values(by=['bytes'])
    threshold=3
    mean_1 = np.mean(df['bytes'])
    std_1 =np.std(df['bytes'])
    # Get IQR
    lower, upper = getIQR(df['bytes'])
    # print(lower)
    # print(upper)
    # Return only values are not outliers
    return (df.loc[df['bytes'].apply(lambda y: (np.abs((y - mean_1)/std_1) <= threshold) & (y <= upper) & (y >= lower) & (y > 0) )])

def totalBytes():
    q = """SELECT projects.*, project_languages.language, project_languages.bytes FROM projects, project_languages
            WHERE project_languages.language = 'python' AND projects.id = project_languages.project_id AND projects.language = 'python' 
            AND deleted != 1 AND bytes % 100 = 0 AND bytes > 1000
            LIMIT 2000"""
    df = query(q)
    
    for i in range(10):
        df = detect_outlier(df)
    
    print(df['bytes'].sum())
    
    df.rename(columns={'id': 'project_id'}, inplace=True)
    df.sort_values('project_id', ascending=True, inplace=True)
    print(df)

    sns.violinplot(df['bytes'])
    plt.show()
    df.to_csv("{0}/totalBytes.csv".format(PATH_CSV), index=False)

def totalCommitsAuthor(project_id):
    q = """SELECT  commits.project_id, author_id, COUNT(commits.id) as total_commit_author
            FROM commits, users
            WHERE commits.project_id IN ({0}) 
            AND users.id = commits.author_id 
            GROUP BY commits.project_id, author_id
            """.format(project_id)
    df = query(q)
    print(df)
    df.to_csv("{0}/totalCommitsAuthor.csv".format(PATH_CSV), index=False)

def totalCommitsProject(project_id):
    q = """SELECT  commits.project_id, COUNT(commits.id) as total_commit_project
            FROM commits
            WHERE commits.project_id IN ({0}) 
            GROUP BY commits.project_id
            ORDER By commits.project_id""".format(project_id)
    df = query(q)
    print(df)
    df.to_csv("{0}/totalCommitsProject.csv".format(PATH_CSV), index=False)

def totalAuthorProject(project_id):
    q = """SELECT commits.project_id, COUNT(DISTINCT users.id) as total_author
            FROM users, commits
            WHERE commits.project_id  IN ({0}) 
            AND users.id = commits.author_id 
            GROUP BY commits.project_id
            ORDER By commits.project_id""".format(project_id)
    df = query(q)

    df = df[['project_id', 'total_author']]
    print(df)
    df.to_csv("{0}/totalAuthor.csv".format(PATH_CSV), index=False)

def majorMinor(project_id):
    totalCommitsProject = pd.read_csv("{0}/totalCommitsProject.csv".format(PATH_CSV))
    totalCommitsAuthor = pd.read_csv("{0}/totalCommitsAuthor.csv".format(PATH_CSV))
    print(totalCommitsProject)
    print(totalCommitsAuthor)
    df = totalCommitsAuthor.merge(totalCommitsProject, on='project_id')
    # print(df)

    df['percent'] = (df['total_commit_author']/df['total_commit_project'])*100
    df.loc[df['percent'] >= 5, 'contributor'] = 'Major' 
    df.loc[df['percent'] < 5, 'contributor'] = 'Minor'

    major = df[df['contributor'] == 'Major'].groupby(['project_id']).size()
    minor = df[df['contributor'] == 'Minor'].groupby(['project_id']).size()

    df_major = pd.DataFrame(major)
    df_minor = pd.DataFrame(minor)

    df = df.merge(df_major, on='project_id') 
    df = df.merge(df_minor, on='project_id', how="left")

    df = df.rename(columns={'0_x': "major"})
    df = df.rename(columns={'0_y': "minor"})
    
    df['minor'] = df['minor'].replace(np.nan, 0).astype(int)
    print(df)

    df.to_csv("{0}/majorMinor.csv".format(PATH_CSV), index=False)

def maxContribution(project_id):
    totalCommitsProject = pd.read_csv("{0}/totalCommitsProject.csv".format(PATH_CSV))
    totalCommitsAuthor = pd.read_csv("{0}/totalCommitsAuthor.csv".format(PATH_CSV))

    df = totalCommitsAuthor.merge(totalCommitsProject, on='project_id')
    df['max_contribution'] = (df['total_commit_author']/df['total_commit_project'])*100


    max = (df.groupby(['project_id']).agg({'max_contribution': 'max'}))
    max.reset_index(inplace=True)
    print(max)

    max.to_csv("{0}/maxContribution.csv".format(PATH_CSV), index=False)

def changeNoExpert(project_id):
    df = pd.read_csv("{0}/majorMinor.csv".format(PATH_CSV))
    
    q = """SELECT * FROM commits
            WHERE commits.project_id  IN ({0}) 
            AND commits.author_id 
            ORDER By commits.project_id""".format(project_id)
    commit = query(q)

    x = df[df['contributor'] == "Minor"].groupby('project_id')['total_commit_author'].sum().reset_index(name = 'total_commit_author')

    y = df.groupby('project_id')['total_commit_author'].sum().reset_index(name = 'total_commit_author')
    # print(y)
    df = pd.merge(x, y, on='project_id', how='right')
    df =df.replace(np.nan, 0).astype(int)
    # print(df)
    df.rename(columns={'total_commit_author_x': 'total_commit_author_minor', 'total_commit_author_y': 'total_commit_project'}, inplace=True)
    df['changeNoExpert'] = 100*df['total_commit_author_minor']/df['total_commit_project']
    print(df)

    df.to_csv("{0}/changeNoExpert.csv".format(PATH_CSV), index=False)

def selfApprChange(project_id):
    totalCommitsProject = pd.read_csv("{0}/totalCommitsProject.csv".format(PATH_CSV))
    #print(totalCommitsProject)
    q = """SELECT project_id, COUNT(commits.id) as total_selfApprChange FROM pull_request_commits
            INNER JOIN commits ON commits.id = pull_request_commits.commit_id
            INNER JOIN pull_request_history ON pull_request_commits.pull_request_id = pull_request_history.pull_request_id
            WHERE action = "merged" AND actor_id = committer_id AND project_id IN ({0}) GROUP BY project_id""".format(project_id)
    df = query(q)
    df = pd.merge(df, totalCommitsProject, on='project_id', how='right')
    df = df.replace(np.nan, 0).astype(int)
    df['percent_selfApprChange'] = (df['total_selfApprChange']/df['total_commit_project'])*100
    print(df)
    df.to_csv("{0}/selfApprChange.csv".format(PATH_CSV), index=False)

def withoutDiscussion(project_id):
    totalCommitsProject = pd.read_csv("{0}/totalCommitsProject.csv".format(PATH_CSV))
    # print(totalCommitsProject)
    q = """SELECT project_id, pull_request_comments.pull_request_id, COUNT(pull_request_comments.commit_id) AS numOfCommits
            FROM pull_request_history
            INNER JOIN pull_request_comments ON pull_request_comments.pull_request_id = pull_request_history.pull_request_id
            INNER JOIN commits ON commits.id = pull_request_comments.commit_id
            WHERE action = "merged" AND project_id IN ({0})
            GROUP BY pull_request_comments.pull_request_id, pull_request_comments.commit_id
            HAVING COUNT(DISTINCT user_id) <= 1
            ORDER BY project_id, pull_request_comments.pull_request_id""".format(project_id)
    df = query(q)
    df = df.groupby(['project_id'])['numOfCommits'].sum()
    df.columns = ['project_id', 'numOfCommits']
    df = pd.merge(df, totalCommitsProject, on='project_id', how='right')
    df = df.replace(np.nan, 0).astype(int)
    df['percent_withoutDiscussion'] = (df['numOfCommits']/df['total_commit_project'])*100
    print(df)
    df.to_csv("{0}/withoutDiscussion.csv".format(PATH_CSV), index=False)

def typicalReviewWindow(project_id):
    q = """ SELECT pull_requests.head_repo_id as project_id, timeopen.pull_request_id as pull_request_id, TIMEDIFF(timeclose.created_at ,timeopen.created_at) as differenttime FROM 
	(SELECT pull_request_id, created_at 
    FROM pull_request_history 
    WHERE pull_request_id IN ( SELECT id as pull_request_id FROM pull_requests WHERE head_repo_id IN ({0})) and action = 'opened') as timeopen,
    (SELECT pull_request_id, created_at 
    FROM pull_request_history 
    WHERE pull_request_id IN ( SELECT id as pull_request_id FROM pull_requests WHERE head_repo_id IN ({0})) and action = 'closed') as timeclose, pull_requests
    WHERE timeopen.pull_request_id = timeclose.pull_request_id AND timeopen.pull_request_id = pull_requests.id""".format(project_id)
    df = query(q)
    # df = df.groupby(['head_repo_id'])['differenttime'].sum()
    # print(df[df['project_id'] == 11161411].head())
    df['differenttime'] = convertTime(df)
    # print(df.groupby(['project_id'])['differenttime'].sum())
    df = df.groupby(['project_id'], as_index=False)['differenttime'].mean()
    df.columns = ['project_id', 'lenghtOfTime']
    print(df)
    
    # Normalized by churn
  
def convertTime(df):
    temp = []
    for index, row in df.iterrows():
        t = row['differenttime'].components
        temp.append(t.days*3600*24 + t.hours*3600 + t.minutes*60 + t.seconds)
    # print(temp)
    # print(df)
    return pd.DataFrame(temp, columns=['differenttime'])

def merge(sample, target):
    merged = pd.merge(sample, target, on='project_id', how='left')
    merged = merged.replace(np.nan, 0)
    return merged

def priorDefects(project_id):
    arr_project_id = [int(i) for i in project_id.split(',')] 
    sample = pd.DataFrame({'project_id': arr_project_id})
    # print(df)
   
    q = """SELECT issues.repo_id, COUNT(DISTINCT issues.id) as numOfPriorDefects, issue_events.action FROM repo_labels
        INNER JOIN issue_labels ON repo_labels.id = issue_labels.label_id
        iNNER JOIN issues ON issue_labels.issue_id = issues.id
        INNER JOIN issue_events ON issue_events.issue_id = issues.id
        WHERE repo_labels.repo_id IN ({0}) AND issue_events.action = "closed"
        GROUP BY issues.repo_id
        """.format(project_id)

    df = query(q)

    merged = pd.merge(sample, df, left_on='project_id', right_on='repo_id', how='left')

    merged = merged.drop('action', 1)
    merged = merged.replace(np.nan, 0).astype(int)
    merged = merged.drop('repo_id', 1)
    print(merged)

    merged.to_csv("{0}/priorDefects.csv".format(PATH_CSV), index=False)

def openPullrequest(project_id, sample):
    q = """SELECT pull_requests.head_repo_id as project_id, COUNT(DISTINCT pull_request_history.pull_request_id) as openPullrequest_count, pull_request_history.action FROM pull_requests
            INNER JOIN pull_request_history ON pull_requests.id = pull_request_history.pull_request_id
            WHERE head_repo_id IN ({0}) 
            AND action = "opened"
            GROUP BY pull_requests.head_repo_id""".format(project_id)
    df = query(q)
    merged = merge(sample, df)
    merged['openPullrequest_count'] = merged['openPullrequest_count'].astype(int)
    merged = merged[['project_id', 'openPullrequest_count']]
    print(merged)
    merged.to_csv("{0}/openPullrequest.csv".format(PATH_CSV), index=False)

def mergedPullrequest(project_id, sample):
    q = """SELECT pull_requests.head_repo_id as project_id, COUNT(DISTINCT pull_request_history.pull_request_id) as mergedPullrequest_count, pull_request_history.action as action FROM pull_requests
            INNER JOIN pull_request_history ON pull_requests.id = pull_request_history.pull_request_id
            WHERE head_repo_id IN ({0}) 
            AND action = "merged"
            GROUP BY pull_requests.head_repo_id""".format(project_id)
    df = query(q)
    merged = merge(sample, df)
    merged['mergedPullrequest_count'] = merged['mergedPullrequest_count'].astype(int)
    merged = merged[['project_id', 'mergedPullrequest_count']]
    print(merged)
    merged.to_csv("{0}/mergedPullrequest.csv".format(PATH_CSV), index=False)

def closedPullrequest(project_id, sample):
    q = """SELECT pull_requests.head_repo_id as project_id, COUNT(DISTINCT pull_request_history.pull_request_id) as closedPullrequest_count, pull_request_history.action as action FROM pull_requests
            INNER JOIN pull_request_history ON pull_requests.id = pull_request_history.pull_request_id
            WHERE head_repo_id IN ({0}) 
            AND action = "closed"
            GROUP BY pull_requests.head_repo_id""".format(project_id)
    df = query(q)
    merged = merge(sample, df)
    merged['closedPullrequest_count'] = merged['closedPullrequest_count'].astype(int)
    merged = merged[['project_id', 'closedPullrequest_count']]
    print(merged)
    merged.to_csv("{0}/closedPullrequest.csv".format(PATH_CSV), index=False)

def openIssue(project_id, sample):
    q = """SELECT issues.repo_id as project_id, COUNT(DISTINCT issues.id) as openIssue_count FROM issues 
            INNER JOIN issue_events ON issue_events.issue_id = issues.id
            WHERE issues.repo_id IN ({0}) 
            AND issue_events.action != "closed"
            GROUP BY issues.repo_id""".format(project_id)
    df = query(q)
    # print(df)
    merged = merge(sample, df)
    merged['openIssue_count'] = merged['openIssue_count'].astype(int)
    merged = merged[['project_id', 'openIssue_count']]
    print(merged)
    merged.to_csv("{0}/openIssue.csv".format(PATH_CSV), index=False)

def closedIssue(project_id, sample):
    q = """SELECT issues.repo_id as project_id, COUNT(DISTINCT issues.id) as closedIssue_count , issue_events.action FROM issues 
            INNER JOIN issue_events ON issue_events.issue_id = issues.id
            WHERE issues.repo_id IN ({0}) 
            AND issue_events.action = "closed"
            GROUP BY issues.repo_id""".format(project_id)
    df = query(q)
    # print(df)
    merged = merge(sample, df)
    merged['closedIssue_count'] = merged['closedIssue_count'].astype(int)
    merged = merged[['project_id', 'closedIssue_count']]
    print(merged)
    merged.to_csv("{0}/closedIssue.csv".format(PATH_CSV), index=False)

def fork(project_id, sample):
    q = """SELECT forked_from as project_id, COUNT(DISTINCT id) as fork_count FROM projects WHERE forked_from IN ({0}) 
            GROUP BY forked_from""".format(project_id)
    df = query(q)

    merged = merge(sample, df)
    merged['fork_count'] = merged['fork_count'].astype(int)
    merged = merged[['project_id', 'fork_count']]
    print(merged)
    
    merged.to_csv("{0}/fork.csv".format(PATH_CSV), index=False)

def getHTML(api_url):
    URL = "{0}".format(api_url)
    # print(URL)

    # sending get request and saving the response as response object 
    headers = {'Authorization': 'token 4fae0c5f5db3a6fe3c24cd9ff7a3581753513b44'}
    r = requests.get(url = URL, headers=headers)
    # extracting data in json format 
    data = r.json()
    return data['html_url']

def getIssues(df):
    op = []
    close = []
    for i in df['url']:
        html = getHTML(i)
        url = "{0}/{1}".format(html, 'issues')
        
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        data = soup.find_all("a", attrs={'class': 'btn-link'})
        # print(data)
        for i in range(2):
            num = data[i].get_text().strip().split(" ")[0]
            if(i == 0):
                op.append(num)
            else:
                close.append(num)
    
    df['open_issue'] = op
    df['close_issue'] = close

    return df

def getPulls(df):
    op = []
    close = []
    for i in df['url']:
        html = getHTML(i)
        url = "{0}/{1}".format(html, 'pulls')
        
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        data = soup.find_all("a", attrs={'class': 'btn-link'})
        # print(data)
        for i in range(2):
            num = data[i].get_text().strip().split(" ")[0]
            if(i == 0):
                op.append(num)
            else:
                close.append(num)
    
    df['open_pull'] = op
    df['close_pull'] = close

    return df
    
def maxDaysWithoutCommits(project_id):
    q = """SELECT project_id, id as commit_id, created_at FROM commits
            WHERE commits.project_id IN ({0})
            ORDER BY commits.created_at
            """.format(project_id)
    df = query(q)
    # 43033531, 52922816
    # print(df)
    ls = []
    projectID = df['project_id'].unique()
    # print(projectID)
    for ID in projectID:
        d = df[df['project_id']==ID]
        d.reset_index(inplace=True)
        # print(d)
        # print(len(d))
        # print(d.size)
        for index, row in d.iterrows():
            # print(index)
            if(len(d) > 1):
                if(index < len(d)-1):
                    before = d.loc[index, "created_at"]
                    # print(before)
                    after = d.loc[index+1, "created_at"]
                    # print(after)
                    day_diff = abs(after - before)
                    # print(day_diff.days)
                    ls.append(day_diff.days)
                    # print("\n")
                else:
                    # print("last index: ".format(index))
                    before = d.loc[index-1, "created_at"]
                    # print(before)
                    after = d.loc[index, "created_at"]
                    # print(after)
                    day_diff = abs(after - before)
                    # print(day_diff.days)
                    ls.append(day_diff.days)
                    # print("\n")
            else:
                ls.append(0)

    df['max_day_diff'] = ls
 
    result = df.groupby("project_id").max()
    # result = result[['max_day_diff']]
    result.reset_index(inplace=True)
    print(result)
    result = result[['project_id', 'max_day_diff']]
    result.to_csv("{0}/maxDaysWithoutCommits.csv".format(PATH_CSV), index=False)


start_time = time.time()
if __name__ == "__main__":
    # Create the main directory for storing csv projects
    df = pd.read_csv("{0}/{1}".format(PATH_CSV, "sample_repo.csv"))
    # df = pd.read_csv("{0}/{1}".format(PATH_CSV, "totalBytes.csv"), index_col=0)
    project_id = convertProjectID(df['project_id'])
    # dataSampling_953projects()
    # print(project_id)
    # totalBytes()
    # totalCommitsAuthor(project_id)
    # totalCommitsProject(project_id)
    # totalAuthorProject(project_id)
    # majorMinor(project_id)
    # maxContribution(project_id)
    # changeNoExpert(project_id)
    # selfApprChange(project_id)
    # withoutDiscussion(project_id)
    # typicalReviewWindow(project_id)
    # merged()
    # priorDefects(project_id)
    # mergedZero()
    # commit = pd.read_csv("/home/senior/senior/csv/totalAuthorProject.csv")
    # mergedPullrequest(project_id)
    # issue = getIssues(df)
    # final = getPulls(issue)
    # print(final)
    # final.to_csv("{0}/dataSampling_final.csv".format(PATH_CSV), index=False)
    # getFork(project_id, df)
    # union()


    # fork(project_id, df)

    # openIssue(project_id, df)
    # closedIssue(project_id, df)

    # openPullrequest(project_id, df)
    # mergedPullrequest(project_id, df)
    # closedPullrequest(project_id, df)

    maxDaysWithoutCommits(project_id)


print("--- %s seconds ---" % (time.time() - start_time))
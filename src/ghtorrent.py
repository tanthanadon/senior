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

PATH_CSV = Path("../csv/368").resolve()

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
            AND users.deleted != 1 AND users.fake != 1
            GROUP BY commits.project_id, author_id
            """.format(project_id)
    df = query(q)
    print(df)
    df.to_csv("{0}/10000/totalCommitsAuthor.csv".format(PATH_CSV), index=False)

def totalCommitsProject(project_id):
    q = """SELECT  commits.project_id, COUNT(commits.id) as total_commit_project
            FROM commits, users
            WHERE commits.project_id IN ({0}) 
            AND users.id = commits.author_id 
            AND users.deleted != 1 AND users.fake != 1
            GROUP BY commits.project_id
            ORDER By commits.project_id""".format(project_id)
    df = query(q)
    print(df)
    df.to_csv("{0}/totalCommitsProject.csv".format(PATH_CSV), index=False)

def dataSampling_953projects():
    projects = pd.read_csv('../csv_368projects/dataSampling_comparedDate.csv')
    # projects = pd.read_csv('../csv_953projects/dataSampling_inactive.csv')
    projects = projects.loc[projects['comparedDate'] == True]
    projects = projects.loc[projects['original_project'] == 'YES']
    print(projects)
    projects.to_csv("{0}/dataSampling_368projects.csv".format(PATH_CSV), index=False)

def totalAuthorProject(project_id):
    q = """SELECT commits.project_id as id, COUNT(DISTINCT users.id) as total_author
            FROM users, commits
            WHERE commits.project_id  IN ({0}) 
            AND users.id = commits.author_id 
            AND users.deleted != 1 AND users.fake != 1
            GROUP BY commits.project_id
            ORDER By commits.project_id""".format(project_id)
    df = query(q)
    # projects = pd.read_csv('../csv_953projects/dataSampling_comparedDate.csv')
    # projects = projects.loc[projects['comparedDate'] == True]
    # print(projects)
    projects = pd.read_csv('../csv_368projects/dataSampling_953projects.csv')
    # projects = pd.read_csv('../csv_953projects/dataSampling_inactive.csv')
    merged = pd.merge(df, projects, on='id', how='right')
    merged = merged.replace(np.nan, 0)
    merged['total_author'] = merged['total_author'].astype(int)
    merged = merged.loc[merged['total_author'] != 0]
    merged = merged.loc[merged['original_project'] == 'YES']
    print(merged)
    merged.to_csv("{0}/dataSampling_368projects.csv".format(PATH_CSV), index=False)

    merged = merged[['id', 'total_author']]
    merged.to_csv("{0}/totalAuthor.csv".format(PATH_CSV), index=False)

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

def ownership(project_id):
    df = pd.read_csv("{0}/majorMinor.csv".format(PATH_CSV))
    max = (df.groupby(['project_id']).agg({'percent': ['max']}))
   
    df = pd.merge(df, max['percent'], on='project_id')
    
    df.loc[df['percent'] >= df['max'], 'ownership'] = 'Yes' 
    df.loc[df['percent'] < df['max'], 'ownership'] = 'No'

    df.rename(columns={"max": "max_ownership"}, inplace=True)
    print(df)

    df.to_csv("{0}/ownership.csv".format(PATH_CSV), index=False)

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

def mergeDF(sample, target):
    merged = pd.merge(sample, target, on='id', how='right')
    merged = merged.replace(np.nan, 0)
    merged['fork_count'] = merged['fork_count'].astype(int)
    merged = merged[['id', 'fork_count']]

def merged():

    df = pd.read_csv('../csv/merged_naturalness_final.csv')
    # df = pd.read_csv('../csv/merged_naturalness_order_mean_final.csv')
    df1 = pd.read_csv('../csv/merged_wily_final.csv')
    merged = df.merge(df1, on='project_id')

    merged = merged[['project_id', 'order', 'cross-entropy', 'Maintainability Index', 'Lines of Code', 'Cyclomatic Complexity']]

    print(merged)
    merged.to_csv("{0}/merged_product.csv".format(PATH_CSV), index=False)
    # merged.to_csv("{0}/merged_product_mean.csv".format(PATH_CSV), index=False)

    merged = merged.drop('Lines of Code', 1)
    merged = merged.drop('Cyclomatic Complexity', 1)

    df2 = pd.read_csv('../csv/selfApprChange.csv')
    df3 = pd.read_csv('../csv/withOutDiscussion.csv')
    merged1 = merged.merge(df2, on='project_id')

    merged1 = merged1.drop('total_selfApprChange', 1)
    merged1 = merged1.drop('total_commit_project', 1)

    merged1 = merged1.merge(df3, on='project_id')
    merged1 = merged1.drop('numOfCommits', 1)
    merged1 = merged1.drop('total_commit_project', 1)


    # print(merged1)
    # merged1.to_csv("{0}/merged_participation.csv".format(PATH_CSV), index=False)
    # merged1.to_csv("{0}/merged_participation_mean.csv".format(PATH_CSV), index=False)

    df4 = pd.read_csv('../csv/changeNoExpert.csv')
    merged2 = merged.merge(df4, on='project_id')

    merged2 = merged2.drop('total_commit_author_minor', 1)
    merged2 = merged2.drop('total_commit_project', 1)

    # print(merged2)
    # merged2.to_csv("{0}/merged_expertise.csv".format(PATH_CSV), index=False)
    # merged2.to_csv("{0}/merged_expertise_mean.csv".format(PATH_CSV), index=False)

    df5 = pd.read_csv('../csv/PriorDefects.csv')



    merged3 = pd.merge(merged, df5, left_on='project_id', right_on='repo_id', how='left')
    merged3 = merged3.drop('action', 1)
    merged3 =merged3.replace(np.nan, 0).astype(int)
    merged3 = merged3.drop('repo_id', 1)

    df6 = pd.read_csv('../csv/merged_churn_final.csv')
    merged3 = merged3.merge(df6, on='project_id')
    merged3 = merged3.drop('add', 1)
    merged3 = merged3.drop('delete', 1)

    # print(merged3)
    # merged3.to_csv("{0}/merged_process.csv".format(PATH_CSV), index=False)
    # merged3.to_csv("{0}/merged_process_mean.csv".format(PATH_CSV), index=False)

    df7 = pd.read_csv('../csv/totalAuthorProject.csv')
    df8 = pd.read_csv('../csv/ownership.csv')

    merged4 = merged.merge(df7, on='project_id')
    merged4 = merged4.merge(df8, on='project_id')

    merged4 = merged4.drop('percent', 1)
    merged4 = merged4.drop('contributor', 1)
    merged4 = merged4.drop('author_id', 1)
    merged4 = merged4.drop('total_commit_author', 1)
    merged4 = merged4.drop('total_commit_project', 1)
    merged4 = merged4.drop('ownership', 1)

    # print(merged4)
    # merged4.to_csv("{0}/merged_human.csv".format(PATH_CSV), index=False)
    # merged4.to_csv("{0}/merged_human_mean.csv".format(PATH_CSV), index=False)

def mergedZero():
    df = pd.read_csv('../csv/changeNoExpert.csv')
    df1 = pd.read_csv('../csv/selfApprChange.csv')
    df2 = pd.read_csv('../csv/withOutDiscussion.csv')
    df3 = pd.read_csv('../csv/priorDefects.csv')


    merged = df.merge(df1, on='project_id')
    merged = merged.merge(df2, on='project_id')
    merged = merged.merge(df3, on='project_id')
    merged = merged[['project_id', 'changeNoExpert', 'percent_selfApprChange', 'percent_withOutDiscussion', 'numOfPriorDefects' ]]
    print(merged)
    merged.to_csv("{0}/mergedZero.csv".format(PATH_CSV), index=False)

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

def getFork(project_id, df):
    # print(df['url'])
    temp = []
    for i in df['url']:
        URL = "{0}".format(i)
        # print(URL)

        # sending get request and saving the response as response object 
        headers = {'Authorization': 'token 4fae0c5f5db3a6fe3c24cd9ff7a3581753513b44'}
        r = requests.get(url = URL, headers=headers)
        # print(r)
        # extracting data in json format 
        data = r.json()
        # print(data)
        # temp.insert(json_normalize(data))
        # print(pd.DataFrame.from_dict(data), orient='index')
        # temp.insert(data)
        # print(data['stargazers_count'])
        try:
            temp.append(data['forks_count'])
        except KeyError:
            temp.append(-1)
    # print(temp)
    df['fork_count'] = temp
    df = df[['id', 'fork_count']]
    print(df)
    df.to_csv("{0}/fork_count.csv".format(PATH_CSV), index=False)

def mergedPullrequest(project_id):
    q = """SELECT pull_requests.head_repo_id as id, COUNT(DISTINCT pull_request_history.pull_request_id) as mergedPullrequest_count, pull_request_history.action as action FROM pull_requests
            INNER JOIN pull_request_history ON pull_requests.id = pull_request_history.pull_request_id
            WHERE head_repo_id IN ({0}) 
            AND action = "merged"
            GROUP BY pull_requests.head_repo_id""".format(project_id)
    df = query(q)
    # print(df)
    projects = pd.read_csv('../csv/dataSampling_1000.csv')
    # print(projects)
    merged = pd.merge(df, projects, on='id', how='right')
    # merged = projects.merge(df, on='id')
    # df = projects.merge(df, on='id')
    merged = merged.replace(np.nan, 0)
    merged['mergedPullrequest_count'] = merged['mergedPullrequest_count'].astype(int)
    merged = merged[['id', 'mergedPullrequest_count', 'action']]
    print(merged)
    df.to_csv("{0}/mergedPullrequest.csv".format(PATH_CSV), index=False)

def openPullrequest(project_id):
    q = """SELECT pull_requests.head_repo_id as id, COUNT(DISTINCT pull_request_history.pull_request_id) as openPullrequest_count, pull_request_history.action FROM pull_requests
            INNER JOIN pull_request_history ON pull_requests.id = pull_request_history.pull_request_id
            WHERE head_repo_id IN ({0}) 
            AND action = "opened"
            GROUP BY pull_requests.head_repo_id""".format(project_id)
    df = query(q)
    # print(df)
    projects = pd.read_csv('../csv/dataSampling_1000.csv')
    # print(projects)
    merged = pd.merge(df, projects, on='id', how='right')
    # merged = projects.merge(df, on='id')
    # df = projects.merge(df, on='id')
    merged = merged.replace(np.nan, 0)
    merged['openPullrequest_count'] = merged['openPullrequest_count'].astype(int)
    merged = merged[['id', 'openPullrequest_count', 'action']]
    print(merged)
    df.to_csv("{0}/openPullrequest.csv".format(PATH_CSV), index=False)

def closedPullrequest(project_id):
    q = """SELECT pull_requests.head_repo_id as id, COUNT(DISTINCT pull_request_history.pull_request_id) as closedPullrequest_count, pull_request_history.action as action FROM pull_requests
            INNER JOIN pull_request_history ON pull_requests.id = pull_request_history.pull_request_id
            WHERE head_repo_id IN ({0}) 
            AND action = "closed"
            GROUP BY pull_requests.head_repo_id""".format(project_id)
    df = query(q)
    # print(df)
    projects = pd.read_csv('../csv/dataSampling_1000.csv')
    # print(projects)
    merged = pd.merge(df, projects, on='id', how='right')
    # merged = projects.merge(df, on='id')
    # df = projects.merge(df, on='id')
    merged = merged.replace(np.nan, 0)
    merged['closedPullrequest_count'] = merged['closedPullrequest_count'].astype(int)
    merged = merged[['id', 'closedPullrequest_count', 'action']]
    print(merged)
    df.to_csv("{0}/closedPullrequest.csv".format(PATH_CSV), index=False)

def closedIssue(project_id):
    q = """SELECT issues.repo_id as id, COUNT(DISTINCT issues.id) as closedIssue_count , issue_events.action FROM issues 
            INNER JOIN issue_events ON issue_events.issue_id = issues.id
            WHERE issues.repo_id IN ({0}) 
            AND issue_events.action = "closed"
            GROUP BY issues.repo_id, issue_events.action""".format(project_id)
    df = query(q)
    # print(df)
    projects = pd.read_csv('../csv/dataSampling_1000.csv')
    # print(projects)
    merged = pd.merge(df, projects, on='id', how='right')
    # merged = projects.merge(df, on='id')
    # df = projects.merge(df, on='id')
    merged = merged.replace(np.nan, 0)
    merged['closedIssue_count'] = merged['closedIssue_count'].astype(int)
    merged = merged[['id', 'closedIssue_count', 'action']]
    print(merged)
    df.to_csv("{0}/closedIssue.csv".format(PATH_CSV), index=False)

def openIssue(project_id):
    q = """SELECT issues.repo_id as id, COUNT(DISTINCT issues.id) as openIssue_count FROM issues 
            INNER JOIN issue_events ON issue_events.issue_id = issues.id
            WHERE issues.repo_id IN ({0}) 
            AND issue_events.action != "closed"
            GROUP BY issues.repo_id""".format(project_id)
    df = query(q)
    # print(df)
    projects = pd.read_csv('../csv/dataSampling_1000.csv')
    # print(projects)
    merged = pd.merge(df, projects, on='id', how='right')
    # merged = projects.merge(df, on='id')
    # df = projects.merge(df, on='id')
    merged = merged.replace(np.nan, 0)
    merged['openIssue_count'] = merged['openIssue_count'].astype(int)
    merged = merged[['id', 'openIssue_count']]
    print(merged)
    df.to_csv("{0}/openIssue.csv".format(PATH_CSV), index=False)

def fork(project_id):
    q = """SELECT forked_from as id, COUNT(DISTINCT id) as fork_count FROM projects WHERE forked_from IN ({0}) 
            GROUP BY forked_from""".format(project_id)
    df = query(q)
    
    print(merged)
    df.to_csv("{0}/fork.csv".format(PATH_CSV), index=False)

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
    
start_time = time.time()
if __name__ == "__main__":
    # Create the main directory for storing csv projects
    df = pd.read_csv("{0}/{1}".format(PATH_CSV, "dataSampling_368projects.csv"))
    # df = pd.read_csv("{0}/{1}".format(PATH_CSV, "totalBytes.csv"), index_col=0)
    project_id = convertProjectID(df['id'])
    # dataSampling_953projects()
    # print(project_id)
    # totalBytes()
    # totalCommitsAuthor(project_id)
    # totalCommitsProject(project_id)
    # totalAuthorProject(project_id)
    # majorMinor(project_id)
    # ownership(project_id)
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

    # mergedPullrequest(project_id)

    # openPullrequest(project_id)
    fork(project_id)

    # closedPullrequest(project_id)
    # closedIssue(project_id)
    # openIssue(project_id)

    


print("--- %s seconds ---" % (time.time() - start_time))
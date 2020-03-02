import mysql.connector
import pandas as pd
from pathlib import Path
import time
import numpy as np
import csv
import seaborn as sns
import matplotlib.pyplot as plt

PATH_CSV = Path("../csv").resolve()

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
    q = """SELECT * FROM projects, project_languages
            WHERE project_languages.language = 'python' AND projects.id = project_languages.project_id AND projects.language = 'python' 
            AND deleted != 1 AND bytes % 100 = 0 AND bytes > 1000
            LIMIT 2000"""
    df = query(q)
    
    for i in range(10):
        df = detect_outlier(df)
    print(df['bytes'].sum())
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
            GROUP BY commits.project_id, author_id""".format(project_id)
    df = query(q)
    print(df)
    df.to_csv("{0}/totalCommitsAuthor.csv".format(PATH_CSV), index=False)

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

def totalAuthorProject(project_id):
    q = """SELECT commits.project_id, COUNT(DISTINCT users.id) as total_author
            FROM users, commits
            WHERE commits.project_id  IN ({0}) 
            AND users.id = commits.author_id 
            AND users.deleted != 1 AND users.fake != 1
            GROUP BY commits.project_id
            ORDER By commits.project_id""".format(project_id)
    df = query(q)
    print(df)
    df.to_csv("{0}/totalAuthorProject.csv".format(PATH_CSV), index=False)

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
    print(totalCommitsProject)
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
    q = """SELECT project_id, pull_request_history.pull_request_id, pull_request_history.created_at AS pull_request_created_at, pull_request_history.action, pull_request_history.actor_id, pull_request_comments.commit_id, pull_request_comments.user_id
            FROM pull_request_history
            INNER JOIN pull_request_comments ON pull_request_comments.pull_request_id = pull_request_history.pull_request_id
            INNER JOIN commits ON commits.id = pull_request_comments.commit_id
            WHERE project_id IN ({0})
            ORDER BY project_id, pull_request_comments.created_at DESC""".format(project_id)
    df = query(q)
    pull_request_id = ' ,'.join(map(str, df['pull_request_id']))
    # print(pull_request_id)
    r = """SELECT timeopen.pull_request_id, TIMEDIFF(timeclose.created_at ,timeopen.created_at) as differenttime FROM 
	(SELECT pull_request_id, created_at 
    FROM pull_request_history 
    WHERE pull_request_id IN ({0}) and action = 'opened') as timeopen,
    (SELECT pull_request_id, created_at 
    FROM pull_request_history 
    WHERE pull_request_id IN ({0}) and action = 'merged') as timeclose
    WHERE timeopen.pull_request_id = timeclose.pull_request_id""".format(pull_request_id)

    x = query(r)
    
    
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

def priorDefects():

    df = pd.read_csv('../csv/totalAuthorProject.csv')
    df1 = pd.read_csv('../csv/PriorDefects.csv')
   
    df = df[['project_id']]
    merged = pd.merge(df, df1, left_on='project_id', right_on='repo_id', how='left')

    merged = merged.drop('action', 1)
    merged = merged.replace(np.nan, 0).astype(int)
    merged = merged.drop('repo_id', 1)
    print(merged)

    merged.to_csv("{0}/priorDefects.csv".format(PATH_CSV), index=False)

def convertProjectID(arr):
    return ' ,'.join(map(str, arr))

def main():
    # Create the main directory for storing csv projects
    # df = pd.read_csv("{0}/{1}".format(PATH_CSV, "sample_repo.csv"), index_col=0)
    df = pd.read_csv("{0}/{1}".format(PATH_CSV, "totalBytes.csv"), index_col=0)
    project_id = convertProjectID(df['project_id'])
    # print(project_id)

    totalBytes()

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
    # priorDefects()
    # mergedZero()

    # commit = pd.read_csv("/home/senior/senior/csv/totalAuthorProject.csv")


start_time = time.time()

main()
print("--- %s seconds ---" % (time.time() - start_time))
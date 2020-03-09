from pathlib import Path
import pandas as pd
import os
from tqdm import tqdm, tnrange, tqdm_pandas
import time
import numpy as np

# Multiprocessing
import logging
import multiprocessing as mp
from multiprocessing_logging import install_mp_handler

def buildWily(PATH_PYTHON):
    # print(PATH_PYTHON)
    os.chdir(str(PATH_PYTHON))
    os.system("wily build .")
    print("########### Building Wily Finished ############")

def prepareHTML(PATH_PYTHON):
    # Components of wily command
    command = "wily report "
    raw = " raw.loc raw.lloc raw.sloc raw.comments raw.multi raw.blank raw.single_comments"
    cc = " cyclomatic.complexity"
    halstead = " halstead.h1 halstead.h2 halstead.N1 halstead.N2 halstead.vocabulary halstead.length halstead.volume halstead.difficulty halstead.effort"
    mi = " maintainability.rank maintainability.mi"
    fragment = " -f HTML -n 1 -o "
    # print(PATH_HTML)
    # print(PATH_SAMPLE)
    # print(PATH_PYTHON)
    projectID = PATH_PYTHON.name
    
    PATH_REPORT = Path(str(PATH_HTML)+"/"+projectID).resolve()
    PATH_REPORT.mkdir(parents=True, exist_ok=True)
    
    # print(PATH_REPORT)

    files = list(PATH_PYTHON.rglob('*.py'))
    # Get into the directory of the target project
    os.chdir(str(PATH_PYTHON))
    # os.system("pwd")
    ID = 0

    for file in files:
        # Get the sub-directory of target file
        target = str(file).split(str(PATH_PYTHON)+"/")[-1]
        #print(target)
        html = str(ID)+".html"
        #print(html)
        wily = command + target + raw + cc + halstead + mi + fragment + str(PATH_REPORT) + "/" + html
        # print(wily)
        # Report all expected metics and save the result as html files in reports folder
        os.system(wily)
        
        ID += 1
    
    print("########### Prepare HTML Finished ############")

def cleanData(df):
    # Remove (0) and (0.0) from table
    df = df.replace(regex={r'\s\(.*': ""})
    
    # Remove "Not found ..." in table
    #df = df.replace(regex={r"\/.*\.[\w:]+": ""})
    df = df.replace(regex={r"^Not found \'.*": str(np.nan)})
    # print(df)
    return df

def convertHTML(PATH_HTML):
    # print(PATH_SUB_HTML)
    #print(PATH_SUB_HTML.name)
    
    projectID = PATH_HTML.name

    # Create folder for storing .csv files by using project ID
    PATH_SUB_METRIC = Path(str(PATH_METRIC)+"/"+projectID)
    PATH_SUB_METRIC.mkdir(parents=True, exist_ok=True)

    temp = pd.DataFrame([])

    #print(PATH_SUB_METRIC)
    files = PATH_HTML.rglob('*.html')
    for file in files:
        # print(files)
        df = pd.read_html(str(file))
        # csv = str(file.name).split(".html")[0]+".csv"
        
        # print(str(PATH_SUB_METRIC)+"/"+csv)
        # print(df[0])

        clean_df = cleanData(df[0])
        
        # print(clean_df)
        temp = temp.append(clean_df, ignore_index=True)

        # Get the metrics of lastest version of a project
        # Export to .csv file
        # df[0].to_csv(str(PATH_SUB_METRIC)+"/"+csv, index=False)
    
    # merge all data file and export them as .csv file for each project
    project = pd.DataFrame(temp)
    project.insert(0, 'project_id', projectID)
    # print(project)
    project.to_csv("{0}/{1}.csv".format(str(PATH_SUB_METRIC), projectID), index=False)
    print("########### Convert HTML Finished ############")

def mergeCSV(PATH_METRIC, PATH_CSV):
    temp = pd.DataFrame([])

    for PATH_SUB_METRIC in tqdm(list(PATH_METRIC.iterdir()), desc="mergeCSV Loop"):
        #print(PATH_SUB_HTML)
        #print(PATH_SUB_HTML.name)
        
        #print(PATH_SUB_METRIC)
        files = list(PATH_SUB_METRIC.rglob('*.csv'))
        
        """
        To merge .csv files in each project
        """
        for file in files:
            #print(file)
            df = pd.read_csv(str(file))
            #print(df)
            temp = temp.append(df)
        #print(temp)
        
    final = pd.DataFrame(temp)
    # print(final)
    final.to_csv(str(PATH_CSV)+"/wily_na.csv", index=False)
    print("########### Merge CSV Finished ############")

def cleanNA(PATH_CSV):
    #print(PATH_CSV)
    df = pd.read_csv(str(PATH_CSV)+"/wily_na.csv")
    df.dropna(inplace=True)
    # print(df.isna())
    print(df)
    df.to_csv(str(PATH_CSV)+"/wily_nona.csv", index=False)
    print("########### Clean NA Finished ############")

def calculateMI(PATH_CSV):
    #print(PATH_CSV)
    df = pd.read_csv(str(PATH_CSV)+"/wily_nona.csv")
    new = df[df.columns[~df.columns.isin(['Date','Maintainability Ranking', 'Maintainability Index','file'])]].groupby('project_id').mean()
    new.reset_index(inplace=True)

    # print("\n###### Maintainability Index #######")
    # print(171-5.2*np.log2(new['Code volume'].head(1))-0.23*new['Cyclomatic Complexity'].head(1)-16.2*np.log2(new['S Lines of Code'].head(1))+50*np.sinc((2.4*(new['Single comment lines']/new['S Lines of Code']))**1/2)[0])
    # np.clip(100 * (171-(5.2*np.log(new['Code volume']))-(0.23*new['Cyclomatic Complexity'])-(16.2*np.log(new['S Lines of Code'])))/171, 0, 100)
    # print(np.clip(100 * (171-(5.2*np.log(new['Code volume']))-(0.23*new['Cyclomatic Complexity'])-(16.2*np.log(new['S Lines of Code'])))/171, 0, 100))
    
    # Find median of MI and merge with df
    new['Maintainability Index'] = np.clip(100 * (171-(5.2*np.log(new['Code volume']))-(0.23*new['Cyclomatic Complexity'])-(16.2*np.log(new['S Lines of Code'])))/171, 0, 100)
    
    print(new)
    # new.to_csv(str(PATH_CSV)+"/mi_med_final.csv", index=False)
    new.to_csv(str(PATH_CSV)+"/wily_final.csv", index=False)

    print("########### Sum Metrics Finished ############")

def dispatch_jobs(func, data):
    # Get the number of CPU cores
    numberOfCores = mp.cpu_count()
    # print(numberOfCores)

    # Data split by number of cores
    # data_split = np.array_split(data, numberOfCores, axis=0)
    # print(type(data_split[0]))

    # set up logging to file
    logging.basicConfig(filename='{0}.log'.format(func), filemode='w', level=logging.DEBUG)
    install_mp_handler()

    with mp.Pool(processes=numberOfCores) as pool:
        length = len(data)
        with tqdm(total=length) as pbar:
            for i, _ in enumerate(pool.map(func, data)):
                pbar.update()
        pool.close()
        pool.join()

    print("########### Dispatch jobs Finished ############")

start_time = time.time()
if __name__ == "__main__":
    # Static Paths
    PATH_SAMPLE = Path("../Sample_Projects/").resolve()
    # Create the main directory for cloning projects
    PATH_SAMPLE.mkdir(parents=True, exist_ok=True)

    PATH_CSV = Path("../csv").resolve()
    # Create the main directory for storing csv projects
    PATH_CSV.mkdir(parents=True, exist_ok=True)

    # Create the directory to store .html files for each project
    PATH_HTML = Path("../all_html/").resolve()
    PATH_HTML.mkdir(parents=True, exist_ok=True)

    # Create the directory to store .csv files of metrics from Wily for each project
    PATH_METRIC = Path("../all_metric/").resolve()
    PATH_METRIC.mkdir(parents=True, exist_ok=True)
    # print(PATH_SAMPLE)

    # Build Wily package into a project
    sample = list(PATH_SAMPLE.iterdir())
    dispatch_jobs(buildWily, sample)
    # buildWily(PATH_SAMPLE)
    
    # Create HTML file from .py files in a project
    sample = list(PATH_SAMPLE.iterdir())
    dispatch_jobs(prepareHTML, sample)
    # print(data)
    
    # Convert all html for each project to .csv file and save them to all_metric folder
    html = list(PATH_HTML.iterdir())
    dispatch_jobs(convertHTML, html)
    # convertHTML(PATH_HTML)

    # # # Measure all .csv file for MI, CC, HV in a project
    mergeCSV(PATH_METRIC, PATH_CSV)
    
    # # # Clean NaN values from wily_na.csv
    cleanNA(PATH_CSV)

    # # Sum all metrics in wily_nona.csv
    calculateMI(PATH_CSV)

print("--- %s seconds ---" % (time.time() - start_time))
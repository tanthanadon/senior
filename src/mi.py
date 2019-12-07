from pathlib import Path
import pandas as pd
import os
from tqdm import trange, tqdm
import time

def buildWily(PATH_SAMPLE):
    for PATH_PYTHON in PATH_SAMPLE.iterdir():
        print(PATH_PYTHON)
        os.chdir(str(PATH_PYTHON))
        os.system("wily build .")
    print("########### Building Wily Finished ############")

def prepareHTML(PATH_SAMPLE, PATH_HTML):
    # Components of wily command
    command = "wily report "
    raw = " raw.loc raw.lloc raw.sloc raw.comments raw.multi raw.blank raw.single_comments"
    cc = " cyclomatic.complexity"
    halstead = " halstead.h1 halstead.h2 halstead.N1 halstead.N2 halstead.vocabulary halstead.length halstead.volume halstead.difficulty halstead.effort"
    mi = " maintainability.rank maintainability.mi"
    fragment = " -f HTML -n 1 -o "
    print(PATH_HTML)
    print(PATH_SAMPLE)
    
    for PATH_PYTHON in PATH_SAMPLE.iterdir():
        projectID= PATH_PYTHON.name
        
        PATH_REPORT = Path(str(PATH_HTML)+"/"+projectID).resolve()
        PATH_REPORT.mkdir(parents=True, exist_ok=True)
        
        print(PATH_REPORT)

        files = list(PATH_PYTHON.rglob('*.py'))
        # Get into the directory of the target project
        os.chdir(str(PATH_PYTHON))
        #os.system("pwd")
        ID = 0
        
        for file in files:
            # Get the sub-directory of target file
            target = str(file).split(str(PATH_PYTHON)+"/")[-1]
            #print(target)
            html = str(ID)+".html" 
            #print(html)
            wily = command + target + raw + cc + halstead + mi + fragment + str(PATH_REPORT) + "/" + html
            #print(wily)
            # Report all expected metics and save the result as html files in reports folder
            os.system(wily)
            ID += 1
    

def convertHTML(PATH_HTML, PATH_METRIC):
    
    for PATH_SUB_HTML in PATH_HTML.iterdir():
        #print(PATH_SUB_HTML)
        #print(PATH_SUB_HTML.name)
        
        projectID= PATH_SUB_HTML.name

        # Create folder for storing .csv files by using project ID
        PATH_SUB_METRIC = Path(str(PATH_METRIC)+"/"+projectID)
        PATH_SUB_METRIC.mkdir(parents=True, exist_ok=True)

        #print(PATH_SUB_METRIC)
        files = list(PATH_SUB_HTML.rglob('*.html'))
        
        for file in tqdm(files, desc="2nd Loop"):
            df = pd.read_html(str(file))
            csv = str(file.name).split(".html")[0]+".csv"
            #print(str(PATH_SUB_METRIC)+"/"+csv)
            #print(df[0])
            # Get the metrics of lastest version of a project
            # Export to .csv file
            df[0].to_csv(str(PATH_SUB_METRIC)+"/"+csv)
    print("########### Convert HTML Finished ############")

def calculateMI(PATH_SUB_METRIC):

def calculateCC(PATH_SUB_METRIC):
    # TCC = Sum(CC) - Count(CC) + 1
    

def calculateHV(PATH_SUB_METRIC):


def mergeCSV(PATH_METRIC):
    for PATH_SUB_METRIC in PATH_METRIC.iterdir():
        #print(PATH_SUB_HTML)
        #print(PATH_SUB_HTML.name)
        
        projectID= PATH_SUB_METRIC.name

        #print(PATH_SUB_METRIC)
        files = list(PATH_SUB_METRIC.rglob('*.csv'))
        
        """
        To calculate
        """

        for file in tqdm(files, desc="2nd Loop"):
            df = pd.read_csv(str(file))
            csv = str(file.name).split(".html")[0]+".csv"
            #print(str(PATH_SUB_METRIC)+"/"+csv)
            print(df['Cyclomatic Complexity'])
            print(df['Maintainability Index'])
            
            # Export to .csv file
            #df[0].to_csv(str(PATH_SUB_METRIC)+"/"+csv)
    print("########### Convert HTML Finished ############")

def main():
    # Statis Paths
    PATH_SAMPLE = Path("../Sample_Projects/").resolve()
    # Create the main directory for cloning projects
    PATH_SAMPLE.mkdir(parents=True, exist_ok=True)

    # Create the directory to store .html files for each project
    PATH_HTML = Path("../all_html/").resolve()
    PATH_HTML.mkdir(parents=True, exist_ok=True)

    # Create the directory to store .csv files of metrics from Wily for each project
    PATH_METRIC = Path("../all_metric/").resolve()
    PATH_METRIC.mkdir(parents=True, exist_ok=True)

    #print(PATH_SAMPLE)

    # Build Wily package into a project
    #buildWily(PATH_SAMPLE) //Okay
    
    # Create HTML file from .py files in a project
    #prepareHTML(PATH_SAMPLE, PATH_HTML) //Okay
    #os.system("pwd")
    
    # Convert all html for each project to .csv file and save them to all_metric folder
    #convertHTML(PATH_HTML, PATH_METRIC) // Okay

    # Measure all .csv file for MI, CC, HV in a project
    mergeCSV(PATH_METRIC)
    

start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
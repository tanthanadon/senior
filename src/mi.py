from pathlib import Path
import pandas as pd
import os
from tqdm import trange, tqdm
import time

def prepareHTML(PATH_PYTHON):
    # Components of wily command
    command = "wily report "
    raw = " raw.loc raw.lloc raw.sloc raw.comments raw.multi raw.blank raw.single_comments"
    cc = " cyclomatic.complexity"
    halstead = " halstead.h1 halstead.h2 halstead.N1 halstead.N2 halstead.vocabulary halstead.length halstead.volume halstead.difficulty halstead.effort"
    mi = " maintainability.rank maintainability.mi"
    fragment = " -f HTML -o ./reports/"

    files = list(PATH_PYTHON.rglob('*.py'))
    # Get into the directory of the target project
    os.chdir(str(PATH_PYTHON))
    os.system("pwd")
    ID = 0
    for file in files:
        # Get the sub-directory of target file
        target = str(file).split(str(PATH_PYTHON)+"/")[-1]
        print(target)
        html = str(ID)+".html" 
        print(html)
        wily = command + target + raw + cc + halstead + mi + fragment + html
        #print(command + target + raw + cc + halstead + mi + fragment + html)
        
        # Report all expected metics and save the result as html files in reports folder
        os.system(wily)

        ID += 1

def convertHTML(PATH_HTML, PATH_METRIC):
    files = list(PATH_HTML.rglob('*.html'))
    for file in files:
        df = pd.read_html(str(file))
        csv = str(file.name).split(".html")[0]+".csv"
        #print(str(PATH_METRIC)+"/"+csv)
        df[0].to_csv(str(PATH_METRIC)+"/"+csv)

def main():
    # Statis Paths
    PATH_SAMPLE = Path("../Sample_Projects/").resolve()
    # Create the main directory for cloning projects
    PATH_SAMPLE.mkdir(parents=True, exist_ok=True)

    print(PATH_SAMPLE)
    for PATH_PYTHON in PATH_SAMPLE.iterdir():
        #print(PATH_PYTHON)
        # Get the name of project from the directory
        projectID = PATH_PYTHON.name
        #print(projectID)

        os.chdir(str(PATH_PYTHON))
        os.system("wily build .")
        '''
        PATH_HTML = Path("../test/all_html/"+projectID).resolve()
        PATH_HTML.mkdir(parents=True, exist_ok=True)

        PATH_REPORT = Path(str(PATH_PYTHON)+"/reports")
        PATH_REPORT.mkdir(parents=True, exist_ok=True)

        PATH_METRIC = Path("../test/all_metric/"+projectID).resolve()
        PATH_METRIC.mkdir(parents=True, exist_ok=True)
        
        print(PATH_PYTHON)
        
        prepareHTML(PATH_PYTHON)
        # Copy all html files for next project
        print("rsync -rv "+str(PATH_REPORT)+"/*.html "+str(PATH_HTML))
        os.system("rsync -rv "+str(PATH_REPORT)+"/*.html "+str(PATH_HTML))
        
        # Convert all html for each project to csv file and save them to all_metric folder
        convertHTML(PATH_HTML, PATH_METRIC)
        '''

start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
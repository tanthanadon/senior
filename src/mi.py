from pathlib import Path
import pandas as pd
import os
from tqdm import trange, tqdm
import time
import numpy as np

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

def mergeCSV(PATH_METRIC, PATH_CSV):
    temp = pd.DataFrame([])
    for PATH_SUB_METRIC in PATH_METRIC.iterdir():
        #print(PATH_SUB_HTML)
        #print(PATH_SUB_HTML.name)
        
        projectID= PATH_SUB_METRIC.name

        #print(PATH_SUB_METRIC)
        files = list(PATH_SUB_METRIC.rglob('*.csv'))
        
        #print(projectID)
        """
        To merge .csv files in each project
        """
        for file in tqdm(files):
            #print(file)
            df = pd.read_csv(str(file)).head(1)
            df['project_id'] = projectID
            df['file'] = str(file)
            df = df.set_index('project_id')
            #print(df)
            temp = temp.append(df)
        #print(temp)
        
    final = pd.DataFrame(temp)
    print(final)
    final.to_csv(str(PATH_CSV)+"/merged_wily.csv", index=False)
    print("########### Merge CSV Finished ############")

def cleanCSV(PATH_CSV):
    print(PATH_CSV)
    df = pd.read_csv(str(PATH_CSV)+"/merged_wily.csv")
    #print(df)
    df.drop(['Unnamed: 0'], axis=1, inplace=True)
    #print(df)
    #print(df.columns)
    #print(df[df.columns[~df.columns.isin(['project_id', 'Revision', 'Author', 'Date', 'Maintainability Ranking', 'file'])]])
    
    # Remove Plus sign(+) from table
    #df = df.replace(regex={r'[+-]': ""})

    # Remove (0) and (0.0) from table
    df = df.replace(regex={r'\s\(.*': ""})
    
    # Remove "Not found ..." in table
    #df = df.replace(regex={r"\/.*\.[\w:]+": ""})
    df = df.replace(regex={r"^Not found \'.*": str(np.nan)})
    #print(df[df[:].isna()==False].count())
    print(df)
    df.to_csv(str(PATH_CSV)+"/merged_wily_na.csv", index=False)
    print("########### Clean CSV Finished ############")

def cleanNA(PATH_CSV):
    print(PATH_CSV)
    df = pd.read_csv(str(PATH_CSV)+"/merged_wily_na.csv")
    df.dropna(inplace=True)
    print(df.isna())
    df.to_csv(str(PATH_CSV)+"/merged_wily_nona.csv", index=False)
    print("########### Clean NA Finished ############")

def sumMetrics(PATH_CSV):
    print(PATH_CSV)
    df = pd.read_csv(str(PATH_CSV)+"/merged_wily_nona.csv", index_col=0)
    print(df.columns)
    new = df[df.columns[~df.columns.isin(['Date','Maintainability Ranking','Maintainability Index','file'])]].groupby('project_id').sum()
    #print(new.columns)
    #print(new)
    # Find Program Length (N)
    #print(new['Length of application'])

    #print(50*np.sinc((2.4*(new['Single comment lines']/new['S Lines of Code']))**1/2))
    #print(new['Multi-line comments']) 
    
    #print(5.2*np.log2(new['Code volume']).head(1))
    #print(0.23*new['Cyclomatic Complexity'].head(1))
    #print(16.2*np.log2(new['S Lines of Code']).head(1))
    #print(50*np.sinc((2.4*(new['Single comment lines']/new['S Lines of Code']))**1/2))
    
    #print(100*(171-5.2*np.log2(new['Code volume'])-0.23*new['Cyclomatic Complexity']-16.2*np.log2(new['S Lines of Code'])+50*np.sinc((2.4*(new['Single comment lines']/new['S Lines of Code']))**1/2))/171)

    new['Maintainability Index'] = df['Maintainability Index'].groupby('project_id').mean()
    print(new)
    new.to_csv(str(PATH_CSV)+"/merged_wily_final.csv")
    print("########### Sum Metrics Finished ############")

def main():
    # Statis Paths
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

    #print(PATH_SAMPLE)

    # Build Wily package into a project
    #buildWily(PATH_SAMPLE) //Okay
    
    # Create HTML file from .py files in a project
    #prepareHTML(PATH_SAMPLE, PATH_HTML) //Okay
    #os.system("pwd")
    
    # Convert all html for each project to .csv file and save them to all_metric folder
    #convertHTML(PATH_HTML, PATH_METRIC) // Okay

    # Measure all .csv file for MI, CC, HV in a project
    #mergeCSV(PATH_METRIC, PATH_CSV)
    
    # Clean data from merged_wily.csv
    #cleanCSV(PATH_CSV)
    
    # Clean NaN values from merged_wily_na.csv
    #cleanNA(PATH_CSV)

    # Sum all metrics in merged_wily_nona.csv
    sumMetrics(PATH_CSV)

start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
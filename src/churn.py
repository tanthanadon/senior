from pathlib import Path
import os
import pandas as pd
from tqdm import trange, tqdm
import time
import matplotlib

def saveText(PATH_SAMPLE, PATH_TEXT):
    #print(PATH_TEXT)
    for file in PATH_SAMPLE.iterdir():
        # Get into the directory of the target project
        os.chdir(str(file))
        command = "git log --numstat --no-merges --pretty= > {0}.txt | mv {0}.txt {1}".format(file.name, PATH_TEXT)
        print(command)
        os.system(command)
    print("########### saveText() Finished ############")

def convert(str):
    if(str == "-"):
        n = 0
    else:
        n = int(str)
    return n

def prepareData(PATH_TEXT, PATH_CSV):
    for file in PATH_TEXT.iterdir():
        #print(file.name.split(file.suffix)[0])
        project_id = file.name.split(file.suffix)[0]
        p = Path(file)
        l = []
        
        for i in p.read_text().split("\n"):
            #print(i)
            dict = {}
            arr = i.split("\t")
            # Find added and deleted lines of each Python file
            if(len(i) != 0 and arr[2].endswith(".py")):
                #print(i.split("\t"))
                dict['project_id'] = project_id
                dict['add'] = convert(arr[0])
                dict['delete'] = convert(arr[1])
                dict['pathname'] = arr[2]
                l.append(dict)
            
        #print(l)
        df = pd.DataFrame.from_dict(l)
        df.to_csv("{0}/{1}.csv".format(PATH_CSV,project_id), index=False)
    print("########### prepareData() Finished ############")

def mergeChurn(PATH_CHURN_CSV, PATH_CSV):
    # print(PATH_CHURN_CSV)
    # print(PATH_CSV)
    df = pd.DataFrame()
    for csv in PATH_CHURN_CSV.iterdir():
        # print(pd.read_csv(str(csv)))
        temp = pd.read_csv(str(csv))
        df = df.append(temp, ignore_index=True)
    # print(df.groupby('project_id').sum())
    #print(df)
    
    # Calculate churn for each project
    churn = df['add'] + df['delete']
    df.insert(3, "churn", churn)
    #print(df)
    # Export merged csv files as merged_churn.csv
    df.to_csv("{0}/merged_churn.csv".format(PATH_CSV), index=False)
    
    # Group rows by project id
    df = df.groupby('project_id').sum()
    df.reset_index(inplace=True)
    #print(df)

    natural = pd.read_csv("{0}/merged_naturalness_final.csv".format(PATH_CSV), index_col=0)
    df = df.merge(natural)
    print(df)

    # Export final version of merged csv files in project level
    df.to_csv("{0}/merged_churn_final.csv".format(PATH_CSV), index=False)
    

def main():
    # Statis Paths
    PATH_SAMPLE = Path("../Sample_Projects/").resolve()
    # Create the main directory for cloning projects
    PATH_SAMPLE.mkdir(parents=True, exist_ok=True)

    PATH_CSV = Path("../csv").resolve()
    # Create the main directory for storing csv projects
    PATH_CSV.mkdir(parents=True, exist_ok=True)

    # Create the directory to store churn values for each project
    PATH_CHURN = Path("../all_churn/").resolve()
    PATH_CHURN.mkdir(parents=True, exist_ok=True)

    PATH_CHURN_TEXT = Path("../all_churn/text/").resolve()
    PATH_CHURN_TEXT.mkdir(parents=True, exist_ok=True)

    PATH_CHURN_CSV = Path("../all_churn/csv/").resolve()
    PATH_CHURN_CSV.mkdir(parents=True, exist_ok=True)

    # Collect the number of added and deleted lines of code from git log for each project
    # And save it as project_id.txt file
    #saveText(PATH_SAMPLE, PATH_CHURN_TEXT)
    
    # Prepare .csv files from .txt files created for each project
    #prepareData(PATH_CHURN_TEXT, PATH_CHURN_CSV)

    # Merge all .csv file and calculate churn for each project
    mergeChurn(PATH_CHURN_CSV, PATH_CSV)

start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
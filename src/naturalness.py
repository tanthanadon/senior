import sys, token, tokenize
from pathlib import Path
import pandas as pd
import numpy as np
# For bash command
import os
# Measure compution time
import time
import re

# Progress bar
from tqdm import trange, tqdm

# Multiprocessing
import multiprocessing as mp

language = "python"
    
# Statis Paths
PATH_SAMPLE = Path("../Sample_Projects/").resolve()
PATH_TOKEN = Path("../all_tokens/").resolve()
PATH_MITLM = Path("~/CacheModelPackage/").expanduser()
PATH_FILES = Path(str(PATH_MITLM)+"/evaluation/data/"+language+"/").resolve()
PATH_OUTPUT = Path(str(PATH_MITLM)+"/evaluation/results/entropy/"+language+"/").resolve()
PATH_ALL = Path("../all_naturalness/").resolve()
PATH_CSV = Path("../csv/").resolve()

# Create the main directory for cloning projects
PATH_SAMPLE.mkdir(parents=True, exist_ok=True)
# Create the main directory for storing token files of all projects
PATH_TOKEN.mkdir(parents=True, exist_ok=True)
# Create the main directory for storing token files in CacheModelPackage porject
PATH_FILES.mkdir(parents=True, exist_ok=True)
# Create the main directory for storing the output from MITLM tool
PATH_OUTPUT.mkdir(parents=True, exist_ok=True)
# Create the main directory for storing csv files of all projects
PATH_ALL.mkdir(parents=True, exist_ok=True)
# Create the main directory for storing the final result of csv files of all projects
PATH_CSV.mkdir(parents=True, exist_ok=True)


def testWritingToken():
    PATH_PYTHON = "/home/thanadon/Documents/Project/Sample Projects/requests/requests"
    PATH_TOKEN = "/home/thanadon/Documents/Project/LanguageModel/tokens/"
    # requests/requests
    p = Path(PATH_PYTHON)
    files = list(p.rglob("*.py"))
    id = 0
    for file in files:
        #print(file)
        name = str(id) + ".py.tokens"
        dir = PATH_TOKEN + name
        print(dir)
        output = Path(dir)
        output.write_text("Test")
        id = id + 1


def tokenization(file):
    with open(file, encoding='utf-8', errors='ignore') as file:
        tokgen = tokenize.generate_tokens(file.readline)
        line = ''
        temp = ''
        for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
            type1 = re.search("^'''", ttext)
            type2 = re.search('^"""', ttext)
            #print(repr(ttext))
            #print(type1)
            #print(type2)
            #print(ttext)
            if ttext != "\n" and bool(type1 or type2) == False:
                if toktype != tokenize.COMMENT:
                    #print(repr(ttext))
                    if toktype == tokenize.STRING:
                        temp = '<str>'
                        
                    else:
                        temp = ttext
                    line = line + temp + ' '
                    #print(repr(temp))
                    
        #print(line)
        return line

def createTokenFile(pythonPath, tokenPath, tokenID):
    tokenLine = tokenization(str(pythonPath))
    fileName = str(tokenID) + ".py.tokens"
    PATH_OUTPUT = str(tokenPath) + "/" + str(fileName)
    output = Path(PATH_OUTPUT)
    # If the file does not exist, it will prepare new files
    with output.open(mode='w+') as file:
            file.write(tokenLine)
            file.close()
    # print(pythonPath.resolve())
    list = [str(pythonPath.resolve()), PATH_OUTPUT]
    return list
    

def prepareToken(PATH_PYTHON, PATH_TOKEN, projectID):
    target = Path(str(PATH_TOKEN)+"/"+projectID+"/")
    target.mkdir(parents=True, exist_ok=True)
    #print(PATH_PYTHON.resolve())
    files = list(PATH_PYTHON.rglob("*.py"))
    d = {}
    tokenID = 0
    pairDirList = []
    for file in files:
        pairDirList = createTokenFile(file, target, tokenID)
        tokenID = tokenID + 1
        d[pairDirList[0]] = pairDirList[1]
    print("############## Tokenization for "+PATH_PYTHON+" finished ################")
    # return d
    
def clearBefore(PATH_TOKEN, PATH_FILES, PATH_OUTPUT):
    #print(PATH_TOKEN)
    #print(PATH_FILES)
    # Remove all fold files for previous project
    os.system("rm -vrdf "+str(PATH_FILES)+"/fold*")

    # Remove all token files for previous project
    os.system("rm -vrdf "+str(PATH_FILES)+"/files/*.tokens")

    # Create new directory first
    q = Path(PATH_FILES+"/files")
    q.mkdir(parents=True, exist_ok=True)

    # Copy all tokens files for next project
    os.system("rsync -rv "+str(PATH_TOKEN)+"*.tokens "+str(q))\

    # Remove sample result in MIT language model
    os.system("rm -rv "+PATH_OUTPUT+"*")
    print("\n############## Clear Before finished #########################")

def calculateEntropy(PATH_MITLM):
    # Get into the directory of MIT language model
    os.chdir(PATH_MITLM+'/evaluation')
    os.system("pwd")
    # Run shell script to calculate entropy for 1-10 grams
    for i in range(1, 11):
        #os.system("sh python_example.sh "+str(i))
        #with 1-10 grams based on input $1
        os.system("mkdir -p ./results/entropy/python/summary")
        os.system("./scripts/train.py ./data/python/ "+str(i)+" 1.0 2")
        os.system("./scripts/cross.py ./data/python/ "+str(i)+" -ENTROPY -BACKOFF -DEBUG -CACHE -CACHE_ORDER "+str(i)+" -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES > ./results/entropy/python/"+str(i)+"gramsCache.txt")
        os.system("./scripts/cross.py ./data/python/ "+str(i)+" -ENTROPY -BACKOFF -DEBUG -FILES > ./results/entropy/python/"+str(i)+"gramsNoCache.txt")
        os.system("python ./scripts/convertCacheResults.py ./results/entropy/python/ ./results/entropy/python/summary/ngrams.csv")

def clearAfter(PATH_OUTPUT, PATH_CSV, projectID):
    
    # Create new directory for storing csv file for each project
    os.system("mkdir -p "+PATH_CSV)
    # Copy summary of results to the original project
    os.system("rsync -rv "+PATH_OUTPUT+"/summary/ "+PATH_CSV)
    # Rename ngram.csv file to project ID
    
    Path(PATH_CSV+"/ngrams.csv").replace(PATH_CSV+"/"+projectID+".csv")
    
    # Remove all summary files for previous project
    os.system("rm -rv "+PATH_OUTPUT+"*")
    
    print("\n############## Clear After finished #########################")

def mergeCSV(PATH_CSV):
    temp = {}
    
    for file in PATH_CSV.glob("*.csv"):
        # Get projectID from file name
        projectID = file.name.split(".csv")[0]
        df = pd.read_csv(file)
        array = []
        
        for i in range(1,16):
            index = "python"+str(i)+"NoCache"
            # Get average cross-entropy for each order of n-grams
            array.append(df[index].mean())
        # Keep array of 1-10 grams into the dictionary
        
        temp[projectID] = array
    
    FINAL_CSV = Path("../csv/").resolve()
    
    # Transpose matrix to set order of n-grams as columns with project IDs as index
    df = pd.DataFrame.from_dict(temp).T
    # Reset index column to be a normal column
    df = df.reset_index()
    
    # print(df.columns[0:])
    
    # Change name index column to project_id
    df.rename(columns=lambda x: x+1 if x in df.columns[1:] else x, inplace = True)
    df.rename(columns={'index': 'project_id'}, inplace=True)
    # print(df)
    
    df = pd.melt(df, id_vars=["project_id"], var_name = ["order"], value_vars=df.columns[1:], value_name="cross-entropy")
    # print(df)
    # Save the final result into ../csv/naturalness_final.csv
    df.to_csv(str(FINAL_CSV)+"/naturalness_original.csv", index=False)
    
    print("########### Merging CSV finished ############")

def mean(PATH_CSV):
    df = pd.read_csv("{0}/naturalness_original.csv".format(PATH_CSV))
    df = df.groupby(['project_id']).mean().reset_index()[['project_id', 'cross-entropy']]
    df.columns = ['project_id', 'cross-entropy_mean']
    # print(df)
    df.to_csv("{0}/naturalness_final.csv".format(PATH_CSV), index=False)

def experiment(PATH_SAMPLE):
    # Loop for all directories
    # check each item is a directory or not
    # dict_token = {}
    for PATH_PYTHON in PATH_SAMPLE:
        #print(PATH_PYTHON)
        if PATH_PYTHON.is_dir():
            try:
                
                # Get the name of project from the directory
                projectID = PATH_PYTHON.name
                #print(projectID)
                
                # Prepare tokens of each project
                # print(PATH_PYTHON)
                prepareToken(PATH_PYTHON, PATH_TOKEN, projectID)
    
                # # mapping directories of Python files with the directories of token files
                # df = pd.DataFrame([(k, v) for k, v in d.items()], columns=['pythonPath', 'tokenPath'])
                # #print(df)
                # dict_token.append(d)

                # # convert dataframe to .csv file
                # df.to_csv("mappingPython2Token.csv")
                
                # Clear all token files of the previous iteration
                clearBefore(str(PATH_TOKEN)+"/"+projectID+"/", str(PATH_FILES), str(PATH_OUTPUT))
                
                calculateEntropy(str(PATH_MITLM))
                
                # Clear all csv files of the previous iteration
                clearAfter(str(PATH_OUTPUT), str(PATH_ALL), projectID)
                
            except:
                continue
                
        else:
            continue

def dispatch_jobs(func, data):
    # Get the number of CPU cores
    numberOfCores = mp.cpu_count()
    # print(numberOfCores)

    # Data split by number of cores
    data_split = np.array_split(data, numberOfCores, axis=0)
    # print(type(data_split[0]))

    with mp.Pool(processes=numberOfCores) as pool:
        length = len(data_split)
        with tqdm(total=length) as pbar:
            for i, _ in enumerate(pool.map(func, data_split)):
                pbar.update()
        pool.close()
        pool.join()

    print("########### Dispatch jobs Finished ############")

start_time = time.time()
if __name__ == "__main__":
    #testTokenization()
    #testWritingToken()
    #testExperiment()

    # Run all functions to calculate crosss-entropy for each project
    sample = list(PATH_SAMPLE.iterdir())
    dispatch_jobs(experiment, sample)

    # Merge .csv file that contains cross-entropy (1-10 grams) for each project
    mergeCSV(PATH_ALL)

    # mean(PATH_CSV)

print("--- %s seconds ---" % (time.time() - start_time))
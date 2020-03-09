from pathlib import Path
import pandas as pd
import os
import logging
import time
import numpy as np

# Multiprocessing
import multiprocessing as mp

# To run external program
import subprocess

# To show progress bar
from tqdm import tqdm

# Static paths
PATH_SAMPLE = Path('../Sample_Projects/').resolve()
PATH_SAMPLE.mkdir(parents=True, exist_ok=True)

PATH_CSV = Path('../csv/').resolve()
PATH_CSV.mkdir(parents=True, exist_ok=True)

#print(PATH_SAMPLE)
print(PATH_CSV)


def getRepo(PATH_CSV):
    # Read API urls from csv file
    
    df = pd.read_csv("{0}/{1}".format(PATH_CSV, "sample.csv"))
    repo = []
    for index, row in df.iterrows():
        repo.append(row['url'].split('https://api.github.com/repos/')[-1])
    #print(temp)
    df['repo'] = pd.DataFrame(repo)
    # Get Purepath and convert to string
    # Save dataframe to csv file
    #print(str(PATH_CSV)+'/sample_repo.csv')
    new_csv = "{0}/{1}".format(PATH_CSV.resolve(), '/sample_repo.csv')
    #print(new_csv)
    df.to_csv(new_csv, index=False)
    print("\n########### Getting repo finished ##############\n")
    

def cloneProject(df):
    # print(df)
    # os.chdir("{0}".format(PATH_SAMPLE))
    # os.system("pwd")

    # set up logging to file
    logging.basicConfig(filename='cloningProject.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')

    for index, row in df.iterrows():
        # Change directory to the sample projects
        # command = "{0}{1}".format("git clone https://github.com/", row['repo'])
        command = "pwd"
        # print(command)
        try:
            # Clone each project to local repository in Sample directory
            subprocess.check_output(command, cwd="{0}".format(PATH_SAMPLE), shell=True)
            # os.system("git clone https://github.com/"+row['repo'])

            project = Path("{0}/{1}".format(PATH_SAMPLE, row['repo'].split("/")[-1]))
            # print(project.exists())
            # Rename the project by project ID
            project.rename("{0}".format(row['project_id']))
        except subprocess.CalledProcessError as callError:
            logging.error(str(callError))
        except FileNotFoundError as fileError:
            logging.error(str(fileError))

    print("\n########### Cloning repo finished ##############\n")

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

    # Get repo for each project and save as csv file
    # getRepo(PATH_CSV)
    
    # Read csv file that contains repository
    # Clone projects to local repositories
    df = pd.read_csv('../csv/sample_repo.csv')

    dispatch_jobs(cloneProject, df)

    # cloneProject(PATH_SAMPLE, df)

print("--- %s seconds ---" % (time.time() - start_time))
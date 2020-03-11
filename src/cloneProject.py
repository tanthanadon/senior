from pathlib import Path
import pandas as pd
import os
import time
import numpy as np

# Multiprocessing
import logging
import multiprocessing as mp
from multiprocessing_logging import install_mp_handler

# To run external program
import subprocess

# To show progress bar
from tqdm import tqdm

# Static paths
PATH_SAMPLE = Path('../Sample_Projects/round_2').resolve()
PATH_SAMPLE.mkdir(parents=True, exist_ok=True)

PATH_CSV = Path('../csv/round_2').resolve()
PATH_CSV.mkdir(parents=True, exist_ok=True)

#print(PATH_SAMPLE)
# print(PATH_CSV)


def getRepo(PATH_CSV):
    # Read API urls from csv file
    
    df = pd.read_csv("{0}/{1}".format(PATH_CSV, "dataSampling_final.csv"))
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

    return df
    
def cloneProject(df):
    project_id = df[0]
    repo = df[-1]

    # Change directory to the sample projects and save as project ID
    command = "{0}{1} {2}".format("git clone https://github.com/", repo, project_id)
    # print(command)
    try:
        # print(command)
        # Clone each project to local repository in Sample directory
        subprocess.check_call(command, cwd="{0}".format(PATH_SAMPLE), shell=True)
        # os.system("git clone https://github.com/"+df)

    except subprocess.CalledProcessError as callError:
        logging.error("CallProcessError: "+str(callError))
    except OSError as osError:
        logging.error("OSError: "+str(osError))

    print("\n########### Cloning repo finished ##############\n")

def dispatch_jobs(func, data):
    # Get the number of CPU cores
    numberOfCores = mp.cpu_count()
    # print(numberOfCores)

    # Data split by number of cores
    # data_split = data
    # print(data_split)
    # data_split = np.array_split(data, numberOfCores, axis=0)
    
    # set up logging to file
    logging.basicConfig(filename='cloningProject.log', filemode='w', level=logging.ERROR)
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

    # Get repo for each project and save as csv file
    repo = getRepo(PATH_CSV)
    
    # Read csv file that contains repository
    # df = pd.read_csv('../csv/sample_repo.csv')

    # Clone projects to local repositories
    data = repo.values.tolist()
    dispatch_jobs(cloneProject, data)

print("--- %s seconds ---" % (time.time() - start_time))
from pathlib import Path
import pandas as pd
import os
import logging



def getRepo(PATH_CSV):
    # Read API urls from csv file
    old_csv = ''
    sample = PATH_CSV.glob('sample.csv')
    for s in sample:
        if s.is_file():
            old_csv = str(s)
        else:
            print("This csv file does not exist")
    print(old_csv)
    
    df = pd.read_csv(old_csv)
    repo = []
    for index, row in df.iterrows():
        repo.append(row['url'].split('https://api.github.com/repos/')[-1])
    #print(temp)
    df['repo'] = pd.DataFrame(repo)
    # Get Purepath and convert to string
    # Save dataframe to csv file
    #print(str(PATH_CSV)+'/sample_repo.csv')
    new_csv = str(PATH_CSV.resolve())+'/sample_repo.csv'
    #print(new_csv)
    df.to_csv(new_csv)
    print("\n########### Getting repo finished ##############\n")
    return df
    

def cloneProject(PATH_SAMPLE, df):
    # Create the main directory for cloning projects
    Path(PATH_SAMPLE).mkdir(parents=True, exist_ok=True)
    os.chdir(PATH_SAMPLE)
    os.system("pwd")
    for index, row in df.iterrows():
        # Clone each project to local repository
        os.system("git clone https://github.com/"+row['repo'])
        logging.basicConfig(filename='gitclone.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info(row['repo'])
        #print(row['repo'])
    print("\n########### Cloning repo finished ##############\n")
    
def main():
    PATH_SAMPLE = Path('../Sample_Projects/').resolve()
    PATH_CSV = Path('../csv/').resolve()
    #print(PATH_SAMPLE)
    print(PATH_CSV)

    # Get repo for each project and save as csv file
    df = getRepo(PATH_CSV)
    
    # Read csv file that contains repository
    # Clone projects to local repositories
    cloneProject(str(PATH_SAMPLE), df)
    

main()
import pandas as pd
import numpy as np
from pathlib import Path
import time

from radon.raw import *
from radon.cli import *
from radon.complexity import *
from radon.metrics import *

import logging

import tqdm

import itertools

from func_timeout import func_timeout, FunctionTimedOut
import signal
import logging

import multiprocessing as mp
from multiprocessing_logging import install_mp_handler

import codecs

# Paths of sample projeects
PATH_SAMPLE = Path("../Sample_Projects/round_2/").resolve()

# Paths of .csv files
PATH_CSV = Path("../csv/round_2/").resolve()

# Path of mi files
PATH_MI = Path("{0}/mi/".format(PATH_CSV)).resolve()
# Create the main directory for cloning projects
PATH_MI.mkdir(parents=True, exist_ok=True)

BASE_CONFIG = Config(
    exclude=r'test_[^.]+\.py',
    ignore='tests,docs',
    include_ipynb=False,
    ipynb_cells=False,
)

CC_CONFIG = Config(
    order=getattr(cc_mod, 'SCORE'),
    no_assert=False,
    min='A',
    max='F',
    show_complexity=False,
    show_closures=False,
    average=True,
    total_average=False,
    **BASE_CONFIG.config_values
)

RAW_CONFIG = Config(
    summary=True,
)

MI_CONFIG = Config(
    multi=True,
    min='B',
    max='C',
    show=True,
    sort=False,
)

def calculateCC(code):
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)

    # Define a timeout for your function (10 seconds)
    signal.alarm(10)

    try:
        arr = mi_parameters(code, count_multi=False)
        CC = arr[1]
        # print(mi_visit(txt, False))
    except SyntaxError:
        CC = -1
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
    return CC

def calculateHV(code):
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)

    # Define a timeout for your function (10 seconds)
    signal.alarm(10)

    try:
        arr = mi_parameters(code, count_multi=False)
        hv = arr[0]
    except SyntaxError:
        hv = -1
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
    return hv

def calculateLOC(code):
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)

    # Define a timeout for your function (10 seconds)
    signal.alarm(10)

    try:
        loc = analyze(code)
        # Module(loc=209, lloc=75, sloc=128, comments=8, multi=36, blank=37, single_comments=8)
        # sloc = loc[2]
    except SyntaxError:
        lst = [-1]
        loc = list(itertools.chain.from_iterable(itertools.repeat(x, 7) for x in lst))
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
    return loc

def calculatePercentComment(code):
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)

    # Define a timeout for your function (10 seconds)
    signal.alarm(10)

    try:
        arr = mi_parameters(code, count_multi=False)
        # Convert percent to radian
        percent = arr[3]*0.06283
    except SyntaxError:
        percent = -1
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
    return percent

def calculateMI(hv, cc, sloc, percent):
    if(hv > 0 and cc > 0 and sloc > 0 and percent > -1):
        real_mi = np.clip(100 * (171-(5.2*np.log(hv))-(0.23*cc)-(16.2*np.log(sloc)))/171, 0, 100)
        # print("MI:")
        # print(100 * (171-(5.2*np.log(hv))-(0.23*cc)-(16.2*np.log(sloc))+(50*np.sin(np.sqrt(2.4*percent))))/171)
        return real_mi
    else:
        return -1

def mergeFile(path_project):
    path = Path(path_project)
    merge = ""
    # Merge all .py files as one file
    # Then, input it into radon API(mi_visit) to calculate MI for each project

    for file in path_project.rglob('*.py'):
        txt = open(str(file)).read()
        merge = merge + "\n" + txt
    return merge

def handler(signum, frame):
    raise Exception("Time Out!")

def evaluate(path_project):
    temp = []
    logging.basicConfig(filename='evaluate.log', filemode='w', level=logging.ERROR)

    # merge = mergeFile(path_project)
    project_id = path_project.name
    files = path_project.rglob("[A-Za-z0-9]*.py")

    for file in files:
        # print(file)
        try:
            code = file.read_text(encoding='ISO-8859-1')
            hv = calculateHV(code)
            # hv = func_timeout(10, calculateHV, args=code)
            cc = calculateCC(code)
            # cc = func_timeout(10, calculateCC, args=code)

            all_loc = calculateLOC(code)
            # all_loc = func_timeout(10, calculateLOC, args=code)

            loc = all_loc[0]
            lloc = all_loc[1]
            sloc = all_loc[2]
            mutli_string = all_loc[3]
            blank = all_loc[4]
            single_comment = all_loc[5]

            percent = calculatePercentComment(code)
            # percent = func_timeout(10, calculatePercentComment, args=code)

            real_mi = calculateMI(hv, cc, sloc, percent)
            # print(real_mi)

            d = {'project_id': path_project.name, 'hv': hv, 'cc': cc, 'loc': loc, 'lloc': lloc, 'sloc': sloc, 'multi_string': mutli_string, 'single_comment': single_comment, 'blank': blank, 'percent': percent, 'mi': real_mi, 'path': str(file)}
            # print(d)
            temp.append(d)
        except Exception as e:
            logging.error("[{0}] project_id: {1}, path: {2}".format(e, project_id, file))
            pass
                
    df = pd.DataFrame(temp, columns=['project_id', 'hv', 'cc', 'sloc', 'percent', 'path']).sort_values('project_id', ascending=True)
    # print(df)
    df.to_csv("{0}/{1}.csv".format(PATH_MI, project_id), index=False)
    return df

def dispatch_jobs(func, data):
    # Get the number of CPU cores
    numberOfCores = mp.cpu_count()
    # print(numberOfCores)

    # Data split by number of cores
    # data_split = np.array_split(data, numberOfCores, axis=0)
    # print(type(data_split[0]))

    # set up logging to file
    logging.basicConfig(filename='mi.log', filemode='w', level=logging.ERROR)
    install_mp_handler()

    with mp.Pool(processes=numberOfCores) as pool:
        max_ = len(data)
        with tqdm.tqdm(total=max_) as pbar:
            result = pool.imap_unordered(func, data)
            for i, _ in enumerate(result):
                pbar.update()
            # result = pool.map(func, data)
            pool.close()
            pool.join()
            result.to_csv("{0}/{1}".format(PATH_CSV, "mi_original.csv"), index=False)
    print("########### Dispatch jobs Finished ############")

start_time = time.time()
if __name__ == "__main__":
    logging.basicConfig(filename='mi.log', filemode='w', level=logging.ERROR)
        
    sample = list(PATH_SAMPLE.iterdir())
    dispatch_jobs(evaluate, sample)

    # Drop the rows where at least one element is missing
    original = pd.read_csv("{0}/{1}".format(PATH_CSV, "mi_original.csv"))
    original.dropna(inplace=True)
    print(original)

    # Average all metrics and calculate MI for each project
    final = original.groupby('project_id').mean()
    final.reset_index(inplace=True)
    final['mi_mean'] = np.clip(100 * (171-(5.2*np.log(final['hv']))-(0.23*final['cc'])-(16.2*np.log(final['sloc'])))/171, 0, 100)
    print(final)
    final.to_csv("{0}/{1}".format(PATH_CSV, "mi_final.csv"), index=False)

print("--- %s seconds ---" % (time.time() - start_time))
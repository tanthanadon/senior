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

import subprocess
import json

import os

# Paths of sample projeects
PATH_SAMPLE = Path("../Sample_Projects/round_2/").resolve()

# Paths of .csv files
PATH_CSV = Path("../csv/round_2/").resolve()

# Path of mi files
PATH_MI = Path("{0}/mi/".format(PATH_CSV)).resolve()
# Create the main directory for cloning projects
PATH_MI.mkdir(parents=True, exist_ok=True)

timeOut = 10

def calculateCC(path):
    # print(path)
    result = subprocess.check_output(['radon', 'cc', '--total-average', path], stderr= subprocess.STDOUT, timeout=timeOut)
    # print(result.decode("utf-8"))
    result_str = result.decode("utf-8")
    if(len(result_str) > 0):
        # Split the last line and collect the data
        output = result_str.split("Average complexity: ")[-1].split(" ")
        # print(result)
        # Rank A - F
        cc_rank = output[0]
        # print(cc_rank)
        # Remove (cc_score) -> cc_score and convert to float value
        cc_score = float(output[1].replace("(", "").replace(")", "").strip())
        # print(cc_score)
    else:
        cc_rank = np.NaN
        cc_score = np.NaN
    
    # print({'cc_rank': cc_rank, 'cc_score': cc_score})
    return {'cc_rank': cc_rank, 'cc_score': cc_score}

def calculateHV(path):
    # print(path)
    result = subprocess.check_output(['radon', 'hal', '-j', path], stderr= subprocess.STDOUT, timeout=timeOut)
    # print(result.decode("utf-8"))
    result_str = result.decode("utf-8")
    # print(stdout.decode("utf-8"))

    # print(stderr)
    x = result_str
    js = json.loads(x)

    hal = js[path]['total']
    
    # print(hal)

    # return array h1, h2, N1, N2, vocabulary, length, calculated_length, volume, difficulty, effort, time, bugs
    # print({'h1': hal[0], 'h2': hal[1], 'N1': hal[2], 'N2': hal[3], 'vocabulary': hal[4], 'length': hal[5], 'calculated_length': hal[6], 'volume': hal[7], 'difficulty': hal[8], 'effort': hal[9], 'time': hal[10], 'bugs': hal[11]})
    return {'h1': hal[0], 'h2': hal[1], 'N1': hal[2], 'N2': hal[3], 'vocabulary': hal[4], 'length': hal[5], 'calculated_length': hal[6], 'volume': hal[7], 'difficulty': hal[8], 'effort': hal[9], 'time': hal[10], 'bugs': hal[11]}

def calculateLOC(path):
    result = subprocess.check_output(['radon', 'raw', '-j', path], stderr= subprocess.STDOUT, timeout=timeOut)
    # print(result.decode("utf-8"))
    result_str = result.decode("utf-8")
    # print(stdout.decode("utf-8"))

    # print(stderr)
    x = result_str
    js = json.loads(x)

    raw = js[path]
    
    # Return dict {'loc': 259, 'lloc': 151, 'single_comments': 48, 'sloc': 149, 'multi': 7, 'comments': 48, 'blank': 55}
    return raw


# def calculateCC(code):
#     # Register the signal function handler
#     signal.signal(signal.SIGALRM, handler)

#     # Define a timeout for your function (10 seconds)
#     signal.alarm(10)

#     try:
#         arr = mi_parameters(code, count_multi=False)
#         CC = arr[1]
#         # print(mi_visit(txt, False))
#     except SyntaxError:
#         CC = -1
#     finally:
#         # Unregister the signal so it won't be triggered
#         # if the timeout is not reached.
#         signal.signal(signal.SIGALRM, signal.SIG_IGN)
#     return CC

# def calculateHV(code, file):
#     # Register the signal function handler
#     signal.signal(signal.SIGALRM, handler)

#     # Define a timeout for your function (10 seconds)
#     signal.alarm(10)

#     try:
#         arr = mi_parameters(code, count_multi=False)
#         hv = arr[0]
#     except SyntaxError:
#         hv = -1
#         print(str(file))
#     finally:
#         # Unregister the signal so it won't be triggered
#         # if the timeout is not reached.
#         signal.signal(signal.SIGALRM, signal.SIG_IGN)
#     return hv

# def calculateLOC(code):
#     # Register the signal function handler
#     signal.signal(signal.SIGALRM, handler)

#     # Define a timeout for your function (10 seconds)
#     signal.alarm(10)

#     try:
#         loc = analyze(code)
#         # Module(loc=209, lloc=75, sloc=128, comments=8, multi=36, blank=37, single_comments=8)
#         # sloc = loc[2]
#     except SyntaxError:
#         lst = [-1]
#         loc = list(itertools.chain.from_iterable(itertools.repeat(x, 7) for x in lst))
#     finally:
#         # Unregister the signal so it won't be triggered
#         # if the timeout is not reached.
#         signal.signal(signal.SIGALRM, signal.SIG_IGN)
#     return loc

# def calculatePercentComment(code):
#     # Register the signal function handler
#     signal.signal(signal.SIGALRM, handler)

#     # Define a timeout for your function (10 seconds)
#     signal.alarm(10)

#     try:
#         arr = mi_parameters(code, count_multi=False)
#         # Convert percent to radian
#         percent = arr[3]*0.06283
#     except SyntaxError:
#         percent = -1
#     finally:
#         # Unregister the signal so it won't be triggered
#         # if the timeout is not reached.
#         signal.signal(signal.SIGALRM, signal.SIG_IGN)
#     return percent

def calculateMI(hv, cc, sloc):
    if(hv != np.NaN and cc != np.NaN and sloc != np.NaN):
        real_mi = np.clip(100 * (171-(5.2*np.log(hv+1))-(0.23*cc)-(16.2*np.log(sloc+1)))/171, 0, 100)
        # print("MI:")
        # print(100 * (171-(5.2*np.log(hv))-(0.23*cc)-(16.2*np.log(sloc)))/171)
        # print(real_mi)
        return real_mi
    else:
        return np.NaN

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

    # merge = mergeFile(path_project)
    project_id = path_project.name
    files = path_project.rglob("[A-Za-z0-9]*.py")

    # print(project_id)
    for file in tqdm.tqdm(list(files), desc="File Level: {0}".format(project_id)):
        print(file)
        if(file.is_file()):
            try:
                path = "{0}".format(file)
                # print(path)
                hv = calculateHV(path)
                # hv = func_timeout(10, calculateHV, args=code)
                cc = calculateCC(path)
                # print(cc)
                # # cc = func_timeout(10, calculateCC, args=code)

                raw = calculateLOC(path)
                # # all_loc = func_timeout(10, calculateLOC, args=code)

                # loc = all_loc[0]
                # lloc = all_loc[1]
                # sloc = all_loc[2]
                # mutli_string = all_loc[3]
                # blank = all_loc[4]
                # single_comment = all_loc[5]

                # percent = calculatePercentComment(code)
                # # percent = func_timeout(10, calculatePercentComment, args=code)

                real_mi = calculateMI(hv['volume'], cc['cc_score'], raw['sloc'])
                # print(hv['volume'], cc['cc_score'], raw['sloc'])
                # print(real_mi)
                # print(file)
                
                
                d = {'project_id': path_project.name}
                d.update(hv)
                d.update(cc)
                d.update(raw)
                d.update({'mi': real_mi})
                d.update({'path': path})
                temp.append(d)
                # logging.info("project_id: {0}, path: {1}".format(project_id, file))
                # print(d)
            except OSError as os:
                logging.error("[{0}], project_id: {1}, path: {2}".format(os, project_id, file))
            except Exception as e:
                logging.error("[{0}], project_id: {1}, path: {2}".format(e, project_id, file))
                pass
        else:
            logging.error("[{0}], project_id: {1}, path: {2}".format("This is not a file", project_id, file))
            pass
                    
    df = pd.DataFrame.from_dict(temp)
    # print(df)
    df.to_csv("{0}/{1}.csv".format(PATH_MI, project_id), index=False)
    # print("########### Finish Calculating MI project: {0} ############".format(project_id))
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
        result = pool.map(func, data)
        pool.close()
        pool.join()
        result.to_csv("{0}/{1}".format(PATH_CSV, "mi_original.csv"), index=False)
    print("########### Dispatch jobs Finished ############")

def contain(id, df):
    flag = False
    for id in df['project_id']:
            if(id == project_id):
                # print(path_project.name)
                flag = True
    return flag

start_time = time.time()
if __name__ == "__main__":
    logging.basicConfig(filename='mi_rerun.log', filemode='w', level=logging.ERROR)

    # f = open("/home/senior/senior/Sample_Projects/round_2/22752448/csw/mgar/gar/v2/lib/python/testdata/javasvn_stats.py", "r")
    # code = f.read()
    # path = "/home/senior/senior/Sample_Projects/round_2/3780176/SublimeCodeIntel.py"
    # # calculateHV(path)
    # calculateCC(path)
    # calculateLOC(path)

    # sample = list(PATH_SAMPLE.iterdir())
    # dispatch_jobs(evaluate, sample)

    # Rerun
    
    rerun = pd.read_csv("/home/senior/senior/src/mi_rerun.csv")
    for path_project in tqdm.tqdm(list(PATH_SAMPLE.iterdir()), desc="Project Level", total=len(rerun)):
        project_id = int(path_project.name)
        temp = []
        if(contain(project_id, rerun)):
            for dirpath, dirs, files in os.walk("{0}".format(path_project)):
                for filename in tqdm.tqdm(list(files), desc="File Level: {0}".format(project_id)):
                    python = os.path.join(dirpath,filename)
                    # print(python)
                    if(python.endswith(".py")):
                        try:
                            path = "{0}".format(python)
                            # print(path)
                            hv = calculateHV(path)
                            # hv = func_timeout(10, calculateHV, args=code)
                            cc = calculateCC(path)
                            # print(cc)
                            # # cc = func_timeout(10, calculateCC, args=code)

                            raw = calculateLOC(path)
                            # # all_loc = func_timeout(10, calculateLOC, args=code)

                            real_mi = calculateMI(hv['volume'], cc['cc_score'], raw['sloc'])

                            d = {'project_id': path_project.name}
                            d.update(hv)
                            d.update(cc)
                            d.update(raw)
                            d.update({'mi': real_mi})
                            d.update({'path': path})
                            temp.append(d)
                            # logging.info("project_id: {0}, path: {1}".format(project_id, file))
                            # print(d)
                        except OSError as os:
                            logging.error("[{0}], project_id: {1}, path: {2}".format(os, project_id, python))
                        except Exception as e:
                            logging.error("[{0}], project_id: {1}, path: {2}".format(e, project_id, python))
        # print(temp)
        df = pd.DataFrame.from_dict(temp)
        # print(df)
        df.to_csv("{0}/{1}.csv".format(PATH_MI, project_id), index=False)

    # Drop the rows where at least one element is missing
    # original = pd.read_csv("{0}/{1}".format(PATH_CSV, "mi_original.csv"))
    # original.dropna(inplace=True)
    # print(original)

    # # Average all metrics and calculate MI for each project
    # final = original.groupby('project_id').mean()
    # final.reset_index(inplace=True)
    # final['mi_mean'] = np.clip(100 * (171-(5.2*np.log(final['hv']))-(0.23*final['cc'])-(16.2*np.log(final['sloc'])))/171, 0, 100)
    # print(final)
    # final.to_csv("{0}/{1}".format(PATH_CSV, "mi_final.csv"), index=False)
    # f = open("/home/senior/senior/Sample_Projects/round_2/194154/python/Lib/test/test_threaded_import.py", "r")
    # print(f.read())
    # print(h_visit(f.read()))

print("--- %s seconds ---" % (time.time() - start_time))
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
    try:
        arr = mi_parameters(code, count_multi=False)
        CC = arr[1]
        # print(mi_visit(txt, False))
    except (SyntaxError):
        CC = np.NaN
    except (FileNotFoundError):
        CC = np.NaN
    return CC

def calculateHV(code):
    try:
        arr = mi_parameters(code, count_multi=False)
        hv = arr[0]
    except (SyntaxError):
        hv = np.NaN
    except (FileNotFoundError):
        hv = np.NaN
    return hv

def calculateLOC(code):
    try:
        loc = analyze(code)
        # Module(loc=209, lloc=75, sloc=128, comments=8, multi=36, blank=37, single_comments=8)
        # sloc = loc[2]
    except (SyntaxError):
        lst = [np.NaN]
        loc = list(itertools.chain.from_iterable(itertools.repeat(x, 7) for x in lst))
    except (FileNotFoundError):
        lst = [np.NaN]
        loc = list(itertools.chain.from_iterable(itertools.repeat(x, 7) for x in lst))
    return loc

def calculatePercentComment(code):
    try:
        arr = mi_parameters(code, count_multi=False)
        # Convert percent to radian
        percent = arr[3]*0.06283
    except (SyntaxError):
        percent = np.NaN
    except (FileNotFoundError):
        percent = np.NaN
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

def evaluate(PATH_SAMPLE):

    temp = []
    for path_project in tqdm.tqdm(list(PATH_SAMPLE.iterdir()), desc="Project Level"):

        # merge = mergeFile(path_project)
        files = path_project.rglob("[A-Za-z0-9]*.py")

        count_multi = False
        for file in tqdm.tqdm(list(files), desc="File Level"):
            # print(file.read_text())
            code = file.read_text()
            hv = calculateHV(code)
            cc      = calculateCC(code)

            all_loc = calculateLOC(code)
            loc = all_loc[0]
            lloc = all_loc[1]
            sloc = all_loc[2]
            mutli_string = all_loc[3]
            blank = all_loc[4]
            single_comment = all_loc[5]

            percent = calculatePercentComment(code)

            real_mi = calculateMI(hv, cc, sloc, percent)
            # print(real_mi)

            d = {'project_id': path_project.name, 'hv': hv, 'cc': cc, 'loc': loc, 'lloc': lloc, 'sloc': sloc, 'multi_string': mutli_string, 'single_comment': single_comment, 'blank': blank, 'percent': percent, 'mi': real_mi}
            # print(d)
            temp.append(d)

    df = pd.DataFrame(temp, columns=['project_id', 'hv', 'cc', 'sloc', 'percent']).sort_values('project_id', ascending=True)
    print(df)
    return df

start_time = time.time()
if __name__ == "__main__":
    logging.basicConfig(filename='mi.log', filemode='w', level=logging.ERROR)
    # Paths of sample projeects
    PATH_SAMPLE = Path("../Sample_Projects/").resolve()

    # Paths of .csv files
    PATH_CSV = Path("../csv/round_1").resolve()

    original = evaluate(PATH_SAMPLE)
    original.to_csv("{0}/{1}".format(PATH_CSV, "mi_original.csv"), index=False)

    # Drop the rows where at least one element is missing
    original.dropna(inplace=True)
    print(original)

    # Average all metrics and calculate MI for each project
    final = original.groupby('project_id').mean()
    final.reset_index(inplace=True)
    final['mi_mean'] = np.clip(100 * (171-(5.2*np.log(final['hv']))-(0.23*final['cc'])-(16.2*np.log(final['sloc'])))/171, 0, 100)
    print(final)
    final.to_csv("{0}/{1}".format(PATH_CSV, "mi_final.csv"), index=False)

print("--- %s seconds ---" % (time.time() - start_time))
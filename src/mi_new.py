import pandas as pd
import numpy as np
from pathlib import Path
import time

from radon.raw import *
from radon.cli import *
from radon.complexity import *
from radon.metrics import *

from pylint import epylint as lint

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

def calculateCC(path_project):
    cc = 0
    p = Path("{0}{1}".format(path_project, "/tests"))
    q = Path("{0}{1}".format(path_project, "/docs"))
    
    for file in path_project.rglob('*.py'):
        if('test' not in str(file) and 'doc' not in str(file) and 'example' not in str(file)):
            # print(file)
            txt = open(str(file)).read()
            try:
                arr = mi_parameters(txt, count_multi=False)
                cc += arr[1]
                # print(mi_visit(txt, False))
            except SyntaxError:
                continue
        # print("CC: {0}".format(cc))
    return cc

def calculateHV(merged_code):
    hv = 0
    try:
        arr = mi_parameters(merged_code, count_multi=False)
        hv = arr[0]
    except SyntaxError:
        hv = -1
    return hv

def calculateSLOC(merged_code):
    # Get SLOC
    sloc = 0
    try:
        loc = analyze(merged_code)
        sloc = loc[2]
    except SyntaxError:
        sloc = -1
    return sloc

def calculatePercentComment(merged_code):
    percent = 0
    try:
        arr = mi_parameters(merged_code, count_multi=False)
        # Convert percent to radian
        percent = arr[3]*0.06283
    except SyntaxError:
        percent = -1
    return percent

def calculateMI(hv, cc, sloc, percent):
    if(hv > -1 and cc > -1 and sloc > -1 and percent > -1):
        real_mi = np.clip(100 * (171-(5.2*np.log(hv))-(0.23*cc)-(16.2*np.log(sloc))+(50*np.sin(np.sqrt(2.4*percent))))/171, 0, 100)
        print("MI:")
        print(100 * (171-(5.2*np.log(hv))-(0.23*cc)-(16.2*np.log(sloc))+(50*np.sin(np.sqrt(2.4*percent))))/171)
        return real_mi
    else:
        return -1

def mergeFile(path_project):
    path = Path(path_project)
    merge = ""
    # Merge all .py files as one file
    # Then, input it into radon API(mi_visit) to calculate MI for each project
    p = Path("{0}{1}".format(path_project, "/tests"))
    q = Path("{0}{1}".format(path_project, "/docs"))
    
    for file in path_project.rglob('*.py'):
        if('test' not in str(file) and 'doc' not in str(file) and 'example' not in str(file)):
            # print(file)
            txt = open(str(file)).read()
            merge = merge + "\n" + txt
    return merge

def evaluate(PATH_SAMPLE):

    temp = []
    for path_project in PATH_SAMPLE.iterdir():

        merge = mergeFile(path_project)

        hv      = calculateHV(merge)
        cc      = calculateCC(path_project)
        sloc    = calculateSLOC(merge)
        percent = calculatePercentComment(merge)

        real_mi = calculateMI(hv, cc, sloc, percent)

        d = {'project_id': path_project.name, 'hv': hv, 'cc': cc, 'sloc': sloc, 'percent': percent, 'mi': real_mi}
        print(d)
        temp.append(d)

    df = pd.DataFrame(temp, columns=['project_id', 'hv', 'cc', 'sloc', 'percent']).sort_values('hv', ascending=True)
    print(df)
    return df

start_time = time.time()
if __name__ == "__main__":
    # Paths of sample projeects
    # PATH_SAMPLE = Path("../Sample_Projects/").resolve()
    path_project = Path("/home/thanadon/senior/Sample_Projects/26427893").resolve()

    # Paths of .csv files
    PATH_CSV = Path("../csv").resolve()
    merge = mergeFile(path_project)

    hv      = calculateHV(merge)
    cc      = calculateCC(path_project)
    sloc    = calculateSLOC(merge)
    percent = calculatePercentComment(merge)

    real_mi = calculateMI(hv, cc, sloc, percent)

    print(hv)
    print(cc)
    print(sloc)
    print(percent)
    print(real_mi)

    # print(mi_visit(merge, False))
    # df = evaluate(PATH_SAMPLE)

    # df.to_csv("{0}/{1}".format(PATH_CSV, "mi_final.csv"), index=False)

print("--- %s seconds ---" % (time.time() - start_time))
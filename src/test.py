import pandas as pd
import numpy as np
from pathlib import Path
import time

from radon.raw import *
from radon.cli import *
from radon.complexity import *
from radon.metrics import *

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

def calculateMI(path_project):
    path = Path(path_project)
    merge = ""
    # Merge all .py files as one file
    # Then, input it into radon API(mi_visit) to calculate MI for each project
    for file in path.rglob('*.py'):
        txt = open(str(file)).read()
        merge = merge + "\n" + txt
            
    # print(merge)
    return {'project_id': path.name, 'mi': mi_visit(txt, True)}

start_time = time.time()
if __name__ == "__main__":
    # Paths of sample projeects
    PATH_SAMPLE = Path("../Sample_Projects/").resolve()

    # Paths of .csv files
    PATH_CSV = Path("../csv").resolve()

    dict = []
    for path in PATH_SAMPLE.iterdir():
        dict.append(calculateMI("{0}".format(path)))
    df = pd.DataFrame(dict, columns=['project_id', 'mi']).sort_values('project_id', ascending=True)
    print(df)

    # df.to_csv("{0}/{1}".format(PATH_CSV, "mi_final.csv"), index=False)

print("--- %s seconds ---" % (time.time() - start_time))
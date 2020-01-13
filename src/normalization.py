import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def main():
    p = Path('../csv/merged_wily_final.csv').resolve()
    q = Path('../csv/merged_naturalness_final.csv').resolve()
    r = Path('../csv/HumanFactor_original.csv').resolve()
    df1 = pd.read_csv(str(p))
    df2 = pd.read_csv(str(q))
    df3 = pd.read_csv(str(r))
    print(df1)
    print(df2)
    print(df3)
    df = df1.merge(df2)
    df = df.apply(np.log)
    print(df[df.columns[~df.columns.isin(['project_id', 'order', 'Unnamed: 0'])]].corr())
    ax = sns.heatmap(df[df.columns[~df.columns.isin(['project_id', 'order', 'Unnamed: 0'])]].corr(), center=0, annot=True)
    plt.show()
    ax.figure.savefig("heatmap_log.png")
    
    
    


main()
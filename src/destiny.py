import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import *
import scipy.stats as scipy

def minmaxScaler(df):
    scaler = MinMaxScaler()
    df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    return df

def standardScaler(df):
    scaler = StandardScaler()
    df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    return df

def calculateMI(df):

    n1 = df['Unique Operators']
    n2 = df['Unique Operands']
    N1 = df['Number of Operators']
    N2 = df['Number of Operands']
    # Halstead Program Length
    N = N1 + N2
    N
    # Halstead Vocabulary
    n = n1 + n2
    n
    # Program Volume
    V = N*np.log2(n)
    df['Code volume'] = V
    # Program Difficulty
    D = (n1/2)*(N2/n2)
    D
    df['Difficulty'] = D
    # Program Effort
    E = D * V
    E
    df['Effort'] = E

    project_id = df['project_id']
    # df = minmaxScaler(df)
    # df = standardScaler(df)
    df[df.columns[~df.columns.isin(['project_id'])]] = df[df.columns[~df.columns.isin(['project_id'])]].apply(np.log)
    HV = df['Effort']
    SLOC = df['S Lines of Code']
    CC = df['Cyclomatic Complexity']
    # print(100 * (171-(5.2*np.log(HV))-(0.23*CC)-(16.2*np.log(SLOC)))/171)
    MI = np.clip(100 * (171-(5.2*np.log(HV))-(0.23*CC)-(16.2*np.log(SLOC)))/171, 0, 100)
    # print(MI)
    df['Maintainability Index'] = MI
    return df
    # df.to_csv("mi_final_normalized.csv", index=False)

def heatmap(df, PATH_PNG):
    fig, ax = plt.subplots(figsize=(20,20))
    sns.heatmap(df.corr(), center=0, annot=True, linewidths=.5, ax=ax)
    plt.show()
    ax.figure.savefig("{0}/heatmap_log_mi_n_order_mean.png".format(PATH_PNG))

def getPearsonr(x, y):
    return scipy.pearsonr(x,y)

def getSpearmanr(x, y):
    return scipy.spearmanr(x,y)

def getPvalue(df):
    # print(df)
    print("##########################")
    order = range(1,16)
    for i in order:
        print(" {0}-gram".format(i))
        x = df[df['order'] == i][['project_id','cross-entropy']]
        y = df[df['order'] == i][['project_id','Maintainability Index']]
        print("Pearson: ",getPearsonr(x['cross-entropy'], y['Maintainability Index']))
        # print("Spearman: ",getSpearmanr(x['cross-entropy'], y['Maintainability Index']))
def getPvalue_mean(df):
    # print(df)
    print("############### Average N and MI ###############")
    print("Pearson: ", getPearsonr(df['cross-entropy_mean'], df['Maintainability Index']))
    # print("Spearman: ",getSpearmanr(x['cross-entropy'], y['Maintainability Index']))

def main():
    PATH_CSV = Path("../csv").resolve()
    # Create the main directory for storing csv projects
    PATH_CSV.mkdir(parents=True, exist_ok=True)

    PATH_PNG = Path('../png/').resolve()

    df = pd.read_csv("{0}/wily_final.csv".format(PATH_CSV))
    n_final = pd.read_csv("{0}/naturalness_final.csv".format(PATH_CSV))
    n_original = pd.read_csv("{0}/naturalness_original.csv".format(PATH_CSV))
    
    mi_final = calculateMI(df)
    # print(mi_final)
    # print(n_final)

    # Average N and MI
    merged_n_mi_final = mi_final.merge(n_final)
    # print(merged_n_mi_final)
    getPvalue_mean(merged_n_mi_final)
    # heatmap(merged_n_mi_final, PATH_PNG)

    # N for each n-gram vs. MI
    merged_n_mi_original = mi_final.merge(n_original)
    # print(merged_n_mi_original)
    getPvalue(merged_n_mi_original)

main()
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def heatmap(df1, df2):
    order = 1
    print(df1)
    print(df2)
    # df = df2
    df = df1.merge(df2)
    print(df[df['order'] == order])
    # take log base e (natural log) into sample data
    df = df[df['order'] == order][df.columns[~df.columns.isin(['project_id', 'order', 'Unnamed: 0'])]].apply(np.log)
    print(df.corr())
    #df = df[['project_id', 'Maintainability Index', 'cross-entropy', 'total_author','total_commit_project','max']].groupby('project_id').apply(np.log)
    #print(df.corr())
    #print(df.corr())
    ax = sns.heatmap(df.corr(), center=0, annot=True)
    plt.show()
    ax.figure.savefig("heatmap_log_mi_n_{0}.png".format(order))

def linear(df1, df2):
    order = 15
    print(df1)
    print(df2)
    # df = df2
    df = df1.merge(df2)
    # print(df)
    df = df[df['order'] == order].apply(np.log)
    print(df)
    ax = sns.regplot(x="Maintainability Index", y="cross-entropy", data=df)
    # g = sns.FacetGrid(df, col="order",  col_wrap=5)
    # g = g.map(sns.regplot, x="Maintainability Index", y="cross-entropy", data=df)
    plt.show()
    ax.figure.savefig("linear_log_mi_n_{0}.png".format(order))

def main():
    p = Path('../csv/merged_wily_final.csv').resolve()
    q = Path('../csv/merged_naturalness_final.csv').resolve()
    r = Path('../csv/HumanFactor_original.csv').resolve()
    df1 = pd.read_csv(str(p))
    df2 = pd.read_csv(str(q), index_col=0)
    df3 = pd.read_csv(str(r), index_col=0)
    # print(df1)
    # print(df2)
    # print(df3)
    #heatmap(df1, df2)
    linear(df1, df2)


main()
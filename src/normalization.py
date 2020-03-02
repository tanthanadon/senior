import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import scipy.stats as scipy

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
    # ax.figure.savefig("heatmap_log_mi_n_{0}.png".format(order))

def linear(df1, df2, png):
    order = 5
    # print(df1)
    # print(df2)
    # df = df2
    df = df1.merge(df2)
    # print(df)
    # df = df[df['order'] == order].apply(np.log)
    # print(df)
    ax = sns.regplot(x="Maintainability Index", y="cross-entropy", data=df[df['order'] == order].apply(np.log))
    ax.figure.savefig("{0}/linear_log_mi_n_{1}.png".format(png, order))
    plt.show()
    # g = sns.FacetGrid(df, col="order",  col_wrap=5)
    # g = g.map(sns.regplot, x="Maintainability Index", y="cross-entropy", data=df)
    # ax.figure.savefig("linear_log_mi_n_{0}.png".format(order))
    # plt.show()
   

def getPearsonr(x, y):
    return scipy.pearsonr(x,y)

def getSpearmanr(x, y):
    return scipy.spearmanr(x,y)

def averageNaturalness(df1, df2, png):
    # df = df[df['project_id'] == 11161411]
    # print(df.mean())
    df1 = df1.groupby(['project_id']).mean().reset_index()[['project_id', 'cross-entropy']]
    df1.columns = ['project_id', 'cross-entropy_mean']
    # print(df1)
    csv = Path("../csv/").resolve()
    df1.to_csv("{0}/merged_naturalness_order_mean_final.csv".format(csv), index=False)
    df = df1.merge(df2)[['cross-entropy_mean', 'Maintainability Index']]
    print(df.corr())
    # ax = sns.heatmap(x="Maintainability Index", y="cross-entropy_mean", data=df)
    # ax.figure.savefig("{0}/linear_log_mi_n_order_mean.png".format(png))
    # ax.figure.savefig("{0}/heatmap_log_mi_n_order_mean.png".format(png))
    plt.show()

def getPvalue(df1, df2):
    df = df1.merge(df2)
    print(df)
    order = range(1,16)
    for i in order:
        x = df[df['order'] == i][['project_id','cross-entropy']]
        y = df[df['order'] == i][['project_id','Maintainability Index']]
        print("Pearson: ",getPearsonr(x['cross-entropy'], y['Maintainability Index']))
        # print("Spearman: ",getSpearmanr(x['cross-entropy'], y['Maintainability Index']))
    x = df[['project_id','cross-entropy']].groupby('project_id').mean().reset_index('project_id')
    y = df[['project_id','Maintainability Index']].groupby('project_id').mean().reset_index('project_id')
    # print(x)
    # print(y)
    print("############### Average N and MI ###############")
    print("Pearson: ",type(getPearsonr(x['cross-entropy'], y['Maintainability Index'])))
    # print("Spearman: ",getSpearmanr(x['cross-entropy'], y['Maintainability Index']))

def main():
    p = Path('../csv/merged_wily_med_final.csv').resolve()
    q = Path('../csv/merged_naturalness_final.csv').resolve()
    r = Path('../csv/HumanFactor_original.csv').resolve()
    png = Path('../png/').resolve()

    wily = pd.read_csv(str(p))
    natural = pd.read_csv(str(q), index_col=0)
    human = pd.read_csv(str(r), index_col=0)
    # print(df1)
    # print(df2)
    # print(df3)
    # heatmap(df1, df2)
    # linear(natural, wily, png)

    # averageNaturalness(natural, wily, png)

    getPvalue(natural, wily)


main()
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
<<<<<<< HEAD
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import numpy as np

from sklearn.preprocessing import quantile_transform
from sklearn.preprocessing import power_transform

def main():
    p = Path('../csv/merged_wily_nona.csv').resolve()
    q = Path('../csv/merged_naturalness.csv').resolve()
    #r = Path('../csv/HumanFactor_final.csv').resolve()

    #df = pd.read_csv("/home/senior/senior/csv/merged_naturalness.csv")


    df = pd.read_csv("/home/senior/senior/csv/merged_wily_nona.csv")
    #df3 = pd.read_csv(str(r))
    #print(df)
    #print(df2)
    #df = df1.merge(df2)
    
    #df = df2.merge(df3)
    #print(df)
    #df = df['Maintainability Index']
    '''
    min_max_scaler = MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(df1)0
    print(x_scaled)
    df = pd.DataFrame(df1)
    '''
    
    #print(df)
    X1 = df.take([1,23], axis=1)
    #print(X1)
    X2 = power_transform(X1, method='yeo-johnson')
    print(X2)
    new = pd.DataFrame(X2, columns=X1.columns)
    print(new)
    
    
    g = sns.FacetGrid(df, col="project_id", col_wrap=5, height=1.5)
    g = g.map(sns.distplot, "Maintainability Index")
    plt.show()
    
    '''
    rng = np.random.RandomState(0)
    X = np.sort(rng.normal(loc=0.5, scale=0.25, size=(25, 1)), axis=0)
    Y = quantile_transform(X, n_quantiles=10, random_state=0, copy=True)
    g = sns.distplot(X)
    plt.show()
    g = sns.distplot(Y)
    plt.show()
    '''
    #g.savefig('output2.png')
=======
from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler, MaxAbsScaler, Normalizer
import numpy as np

def main():
    df = pd.read_csv("/home/thanadon/senior/csv/merged_wily_nona.csv")
    scaler = RobustScaler()
    test = df[df['project_id'] == 11161411]["Maintainability Index"]
    scaler.fit(test.to_numpy().reshape(-1,1))
    x = scaler.transform(test.to_numpy().reshape(-1,1))
    ax = sns.countplot(x="Maintainability Index", data=df)
    print(df)
    plt.show()
    '''
    old = df
    old[old["project_id"]==56604179]["Maintainability Index"].hist()
    plt.show()
    new = df
    new["Maintainability Index"] = np.log(df[df['Maintainability Index'] != 0]['Maintainability Index'])
    new[new["project_id"]==56604179]["Maintainability Index"].hist()
    plt.show()
    '''
    '''
    print(x)
    plt.hist(x, density=True, range=[0,5])
    plt.show()
    '''
    
    '''
    
    f = sns.FacetGrid(old[['project_id', 'Maintainability Index']], col="project_id", col_wrap=5, height=1.5)
    f = f.map(sns.distplot, "Maintainability Index")
    plt.show()
    f.savefig("output_nolog.png")
    
    g = sns.FacetGrid(new[['project_id', 'Maintainability Index']], col="project_id", col_wrap=5, height=1.5)
    g = g.map(sns.distplot, "Maintainability Index")
    plt.show()
    g.savefig('output_loge.png')
    '''
    
>>>>>>> bc08f317f3e118b4a75a2f07bcffa793453a5c33

main()
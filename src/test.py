import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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
    

main()
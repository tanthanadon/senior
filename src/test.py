import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler, MaxAbsScaler, Normalizer
import numpy as np

def main():
    df = pd.read_csv("/home/thanadon/senior/csv/merged_wily_nona.csv")
    # scaler = RobustScaler()
    # test = df[df['project_id'] == 11161411]["Maintainability Index"]
    # scaler.fit(test.to_numpy().reshape(-1,1))
    # x = scaler.transform(test.to_numpy().reshape(-1,1))
    # ax = sns.countplot(x="Maintainability Index", data=df)
    df["Maintainability Index"] = np.log(df[df['Maintainability Index'] != 0]['Maintainability Index'])
    '''
    print(x)
    plt.hist(x, density=True, range=[0,5])
    plt.show()
    '''
    '''
    sns.distplot(test)
    plt.show()
    sns.distplot(x)
    plt.show()
    '''
    
    g = sns.FacetGrid(df[['project_id', 'Maintainability Index']], col="project_id", col_wrap=5, height=1.5)
    g = g.map(sns.distplot, "Maintainability Index")
    plt.show()
    
    #g.savefig('output.png')
    

main()
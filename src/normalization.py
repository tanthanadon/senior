import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    p = Path('../csv/merged_wily_final.csv').resolve()
    q = Path('../csv/merged_naturalness.csv').resolve()
    r = Path('../csv/HumanFactor_final.csv').resolve()
    df1 = pd.read_csv(str(p))
    df2 = pd.read_csv(str(q))
    df3 = pd.read_csv(str(r))
    #print(df1)
    #print(df2)
    #df = df1.merge(df2)
    
    #df = df2.merge(df3)
    #print(df)
    #df = df['Maintainability Index']
    min_max_scaler = MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(df3)
    df = pd.DataFrame(x_scaled, columns=df3.columns)
    test = df[['cross-entropy','total_author','total_commit_project','max','major','minor']].corr()
    print(test)
    ax = sns.heatmap(test, center=0)
    plt.show()
    #print(preprocessing.normalize(df['Lines of Code']))
    
    #print(df.corr()['Maintainability Index'])


main()
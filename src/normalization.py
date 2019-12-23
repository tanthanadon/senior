import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    df1 = pd.read_csv("/home/thanadon/senior/csv/merged_wily_final.csv")
    df2 = pd.read_csv("/home/thanadon/senior/csv/merged_naturalness.csv")
    #print(df1)
    #print(df2)
    df = df1.merge(df2)
    #df = df['Maintainability Index']
    min_max_scaler = MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(df)
    df = pd.DataFrame(x_scaled, columns=df.columns)
    test = df[['Maintainability Index', 'cross-entropy']].corr()[['Maintainability Index', 'cross-entropy']]
    ax = sns.heatmap(test, center=0)
    plt.show()
    #print(preprocessing.normalize(df['Lines of Code']))
    
    #print(df.corr()['Maintainability Index'])


main()
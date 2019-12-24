import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv("/home/senior/senior/csv/merged_naturalness.csv")
    g = sns.FacetGrid(df, col="project_id", col_wrap=5, height=1.5)
    g = g.map(plt.plot, "order", "cross-entropy", marker=".")
    plt.show()
    g.savefig('output.png')

main()
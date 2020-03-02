import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    PATH_CSV = Path("../csv").resolve()
    # Create the main directory for storing csv projects
    PATH_CSV.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv("{0}/merged_churn.csv".format(PATH_CSV))
    # df = df[df['project_id'] == 11161411]
    # print(df['churn'].quantile(q=0.75)-df['churn'].quantile(q=0.25))
    df = df.groupby("project_id")
    print(df['churn'].quantile(q=0.75)-df['churn'].quantile(q=0.25))

main()
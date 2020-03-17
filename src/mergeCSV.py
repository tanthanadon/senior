import pandas as pd
from pathlib import Path

if __name__ == "__main__":
    # Paths of .csv files
    PATH_CSV = Path("../csv/round_2").resolve()
    PATH_FACTOR = Path("../csv/round_2/factor").resolve()

    temp = pd.read_csv("/home/senior/senior/csv/round_2/sample_repo.csv")
    temp = temp['project_id']

    # maxDayWithOutCommit = pd.read_csv("/home/senior/senior/csv/round_2/factor/maxDaysWithoutCommits.csv")
    # maxDayWithOutCommit = maxDayWithOutCommit[['project_id', 'max_day_diff']]
    # print(maxDayWithOutCommit)
    # maxDayWithOutCommit.to_csv("/home/senior/senior/csv/round_2/factor/maxDaysWithoutCommits.csv", index=False)

    for path in PATH_FACTOR.iterdir():
        df = pd.read_csv("{0}".format(path))
        print(df)
        temp = pd.merge(temp, df, how="inner", on="project_id")
    print(temp)
    temp.to_csv("{0}/merge_all.csv".format(PATH_CSV), index=False)
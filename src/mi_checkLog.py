from pathlib import Path
import pandas as pd
import numpy as np

if __name__ == "__main__":
    
    sample = pd.read_csv("/home/senior/senior/csv/round_2/sample_repo.csv")

    path = Path("log.txt")
    # print(path.read_text())
    arr = path.read_text().split("\n")
    temp = []

    for row in arr:
        try:
            # print(row.strip())

            # Check the output that related to File Level progress bar
            if(row.split(": ")[0].startswith("File Level")):
                project_id = int(row.split(": ")[1].strip())
                percent = row.split(": ")[2]
                
                # check the completeness of calculation and assign success status
                if(percent.startswith("100%")):
                    temp.append({"project_id": project_id, "mi_success": True})
                else:
                    temp.append({"project_id": project_id, "mi_success": False})
                    print(project_id, percent)
                # print(row.split(": ")[1])
            else:
                # print(row)
                pass
        except IndexError:
            # print(row)
            pass
    
    # print(temp)
    df = pd.DataFrame(temp)
    # print(df.columns)

    merge = pd.merge(sample, df, how="left", on="project_id")
    
    # Replaec NaN value in column "mi_success" as False
    values = {"mi_success": False}
    merge.fillna(value=values, inplace=True)
    print(merge)

    # Count the number of incompleted caculating projects
    number_error_project = merge[merge['mi_success'] == False]['mi_success'].count()
    print("Percent of error: {}".format(number_error_project/356*100))
    # print(merge[merge['mi_success'] == False][['project_id', 'bytes']])

    # Export only projects where their success status are false
    final = merge[merge['mi_success'] == False][['project_id', 'mi_success']]
    # print(final)
    final.to_csv("mi_rerun.csv", index=False)

    
        
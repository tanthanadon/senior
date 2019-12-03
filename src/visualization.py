import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../csv/merged_naturalness.csv", header=0, names=['project_id', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], index_col=['project_id'])
print(df.loc[:])
#41010830
#34561609
x = range(1,11)
#print(df.loc[34561609])
fig = plt.figure()
for index, row in df.iterrows():
    plt.plot(x, df.loc[index],  marker='o', markersize=5)
#plt.plot( index, '1', data=df, marker='', color='olive', linewidth=2, linestyle='dashed', label="toto")
plt.show()
fig.savefig("naturalness.png")

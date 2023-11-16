import pandas as pd
df1=pd.read_csv("Berlin_mitte_metrics.csv")
df2=pd.read_csv("Berlin_N.csv")

df1['id'] = df1['id'].astype(str)
df2['co_id'] = df2['co_id'].astype(str)
# 现在左侧和右侧的'id'列应该具有相同的数值数据类型
print(df1.head())
print(df2.head())
merged_df = df1.merge(df2, left_on='id', right_on='co_id', how='left')
merged_df.to_csv("_5Berlin_features.csv")
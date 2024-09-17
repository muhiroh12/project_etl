import pandas as pd

path_csv ='/opt/airflow/dags/input/customer_info.csv'

df = pd.read_csv(path_csv)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

def filter(df):
    return df[df['country'] == 'Australia']
    
filtered_df = filter(df)
filtered_df.to_csv('/opt/airflow/dags/output/test_output_bash.csv', index=False)
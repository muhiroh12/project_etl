import pandas as pd
from sqlalchemy import create_engine

# Define the database URI
db_uri = 'postgresql+psycopg2://postgres:admin@host.docker.internal:5432/airflow_data_retail'

# Create an SQLAlchemy engine
engine = create_engine(db_uri)

# Execute the SQL query using read_sql_query and store the result in a DataFrame
read_test = pd.read_sql_table('test_airflow', engine)

# Save the DataFrame to a CSV file
read_test.to_csv('/opt/dags/output/test_postgres.csv', index=False)

# Load data from CSV file to database
def load_to_database(df, table_name):
    try:
        df.to_sql(name=table_name, con=engine, index=False, if_exists='replace')
    except Exception as e:
        print(f'Error loading data to database: {e}')

# Load data to database
load_to_database(read_test, 'test_airflow')

# Close the engine connection if needed (depending on context)
engine.dispose()
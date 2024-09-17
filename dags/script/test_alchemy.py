from sqlalchemy import create_engine
import pandas as pd

db_uri = 'postgresql+psycopg2://airflow:airflow@host.docker.internal:5434/test_database'
engine = create_engine(db_uri)

df = pd.DataFrame({'column1': [1, 2], 'column2': ['a', 'b']})

# Use the SQLAlchemy connection directly
try:
    with engine.connect() as conn:
        df.to_sql(name='example_table', con=conn, index=False, if_exists='replace')
    print("Data loaded successfully")
except Exception as e:
    print(f'Error loading data to database: {e}')

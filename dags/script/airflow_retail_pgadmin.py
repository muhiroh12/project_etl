import pandas as pd
import glob
from pandasql import sqldf
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
#from sqlalchemy import create_engine


#Read CSV file
class CSVReader:
    def __init__(self,filepath):
        self.filepath = filepath
        
    def read_csv_file(self):
        try:
            if "customer_info" in self.filepath:
                df = pd.read_csv(self.filepath, skip_blank_lines=True)
            else:
                allfiles = glob.glob(self.filepath)
                df = pd.concat([pd.read_csv(file, skip_blank_lines=True) for file in allfiles])
            return df
        except FileNotFoundError:
            print(f'Error: the file {self.filepath} was not found')
            return None
        except pd.errors.EmptyDataError:
            print(f'Error: the file {self.filepath} is empty')
            return None
        except pd.errors.ParserError as e:
            print(f'Error: An error occured while parsing the file {self.filepath} : {e}')
            return None
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
        
#Cleaning data
class DataCleaner:
    def __init__(self, df, filepath):
        self.df = df
        self.filepath = filepath
        
    def clean_data(self):
        self.df = self.remove_unnamed_column()
        self.df = self.convert_date()
        self.df = self.remove_null_data()
        self.df = self.remove_duplicate_data()
        return self.df
    
    def remove_unnamed_column(self):
        return self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]
    
    def convert_date(self):
        if "product" in self.filepath:
            date_column = ['invoice_date']
        elif "customer_info" in self.filepath:
            date_column = []
        else:
            raise ValueError("Unknown filename")
        
        for column in date_column:
            if column in self.df.columns:
                self.df[column] = pd.to_datetime(self.df[column])
        return self.df
    
    def remove_null_data(self):
        return self.df.dropna()
    
    def remove_duplicate_data(self):
        if "customer_info" in self.filepath:
            self.df = self.df.sort_values(by='customer_id').drop_duplicates(subset='customer_id', keep='first')
        elif "product" in self.filepath:
            self.df = self.df.sort_values(by='product_id').drop_duplicates(subset='product_id', keep='first')
        return self.df

#Mapping data for product
class MappingDataProduct:
    def __init__(self, df, filepath):
        self.df = df
        self.filepath = filepath
    
    def create_location_for_product(self):
        if "product" in self.filepath:
            lower_product_group = self.df.copy()
            lower_product_group.loc[:, 'product_group'] = self.df['product_group'].str.lower()  # Gunakan .loc[] di sini
            # Define location based on product_group
            location_map = {
                'accessories': 'Lt.2_Stand.1_accessories',
                'bag': 'Lt.2_Stand.4_bag',
                'box': 'Lt.1_Stand.1_box',
                'cloth': 'Lt.2_Stand.5_cloth',
                'electronic': 'Lt.1_Stand.2_electronic',
                'glassware': 'Lt.1_Stand.3_glassware',
                'kitchenware': 'Lt.1_Stand.4_kitchenware',
                'personal hygene': 'Lt.2_Stand.6_personal hygene',
                'stationery': 'Lt.2_Stand.2_stationery',
                'utensil': 'Lt.1_Stand.7_utensil',
                'tools': 'Lt.1_Stand.6_tools',
                'toy': 'Lt.2_Stand.3_toy'
            }
            # Map product_group ke location
            lower_product_group.loc[:, 'location'] = lower_product_group['product_group'].map(location_map).fillna('not register yet')  # Gunakan .loc[] di sini

            # Select the relevant columns
            #result_product = dedup_data_retail_cleanup[['product_id', 'product_group', 'location']]
            self.df = lower_product_group[['product_name', 'location']].copy()
            self.df.loc[:, 'productID'] = range(1, len(self.df)+1)
        else:
            pass
        return self.df

class LoadToDatabase:
    def __init__(self, postgres_conn_id, table_name):
        self.postgres_conn_id = postgres_conn_id
        self.table_name = table_name

    def create_tables(self):
        try:
            # Create table based on the table name
            hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            connection = hook.get_conn()
            cursor = connection.cursor()

            if self.table_name == 'customer':
                create_table_query = """
                CREATE TABLE IF NOT EXISTS customer (
                    customer_id SERIAL PRIMARY KEY,
                    customer_name VARCHAR(255),
                    email_address VARCHAR(255),
                    country VARCHAR(50),
                    phone VARCHAR(20)
                );
                """
            elif self.table_name == 'product':
                create_table_query = """
                CREATE TABLE IF NOT EXISTS product (
                    productID SERIAL PRIMARY KEY,
                    product_name VARCHAR(255),
                    location VARCHAR(255)
                );
                """
            else:
                raise ValueError(f"Unknown table: {self.table_name}")

            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
            connection.close()

            print(f'Successfully created table {self.table_name}')
        except Exception as e:
            print(f'Error creating table: {e}')

    def load_to_database(self, df):
        try:
            # Convert dataframe to list of tuples
            data_tuples = [tuple(x) for x in df.to_numpy()]

            # Get column names from the dataframe
            columns = ', '.join(df.columns)

            # Create the upsert query
            if self.table_name == 'customer':
                upsert_query = f"""
                INSERT INTO {self.table_name} ({columns}) VALUES %s
                ON CONFLICT (customer_id) DO UPDATE SET
                customer_name = EXCLUDED.customer_name,
                email_address = EXCLUDED.email_address,
                country = EXCLUDED.country,
                phone = EXCLUDED.phone;
                """
            elif self.table_name == 'product':
                upsert_query = f"""
                INSERT INTO {self.table_name} ({columns}) VALUES %s
                ON CONFLICT (productID) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                location = EXCLUDED.location;
                """

            # Use PostgresHook to connect to the database
            hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            connection = hook.get_conn()
            cursor = connection.cursor()

            # Execute batch upsert using psycopg2's execute_values
            from psycopg2.extras import execute_values
            execute_values(cursor, upsert_query, data_tuples)

            # Commit the transaction
            connection.commit()
            cursor.close()
            connection.close()

            print(f'Successfully upserted data into {self.table_name}')
        except Exception as e:
            print(f'Error upserting data to database: {e}')
    
def main():
    file_to_table_map = {
        'customer_info.csv': 'customer',
        'product_*.csv': 'product'
    }
    
    for file, table_name in file_to_table_map.items():
        csv_reader = CSVReader(f'/opt/airflow/dags/input/{file}')
        df = csv_reader.read_csv_file()
        if df is not None:
            data_cleaner = DataCleaner(df, f'/opt/airflow/dags/input/{file}')
            df = data_cleaner.clean_data()
            mapping_data_product = MappingDataProduct(df, f'/opt/airflow/dags/input/{file}')
            df = mapping_data_product.create_location_for_product()

            # Create the database loader
            database_loader = LoadToDatabase(postgres_conn_id='retail_connection', table_name=table_name)

            # Call create_tables before loading data
            database_loader.create_tables()

            # Load data into the database
            database_loader.load_to_database(df)

if __name__ == "__main__":
    main()

import pandas as pd
import glob
from pandasql import sqldf
from sqlalchemy import create_engine

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
            self.df = lower_product_group[['product_group', 'location']].copy()
            self.df.loc[:, 'productID'] = range(1, len(self.df)+1)
        else:
            pass
        return self.df

class LoadToDatabase:
    def __init__(self, engine, table_name):
        self.engine = engine
        self.table_name = table_name
    
    def load_to_database(self, df):
        try:
            with self.engine.connect() as connection:
                df.to_sql(name=self.table_name, con=connection, index=False, if_exists='replace')
        except Exception as e:
            print(f'Error loading data to database: {e}')
        
def main():
    file_to_table_map = {
        'customer_info.csv': 'customer',
        'product_*.csv': 'product'
    }
    db_uri = 'postgresql+psycopg2://postgres:admin@host.docker.internal:5432/airflow_data'
    connection_string = f'postgresql://{db_uri.split("://")[1]}'
    engine = create_engine(connection_string)
    
    for file, table_name in file_to_table_map.items():
        csv_reader = CSVReader(f'./dags/input/{file}')
        df = csv_reader.read_csv_file()
        if df is not None:
            data_cleaner = DataCleaner(df, f'./dags/input/{file}')
            df = data_cleaner.clean_data()
            mapping_data_product = MappingDataProduct(df, f'./dags/input/{file}')
            df = mapping_data_product.create_location_for_product()
            database_loader = LoadToDatabase(engine, table_name)
            database_loader.load_to_database(df)
            
if __name__ == "__main__":
    main()
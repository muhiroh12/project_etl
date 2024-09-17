import pandas as pd
import numpy as np
from pandasql import sqldf
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import calendar
import glob

class RetailDataCustomer:
    def __init__(self, customer_csv):
        self.customer_csv = customer_csv
        self.customer_data = None
        
    #Read data customer from csv
    def read_customer_csv(self):
        try:
            rd_customer = pd.read_csv(self.customer_csv, skip_blank_lines=True)
            rd_customer = rd_customer.loc[:, ~rd_customer.columns.str.contains('^Unnamed')]
            self.customer_data = rd_customer[rd_customer['phone'].notnull()]
            return self.customer_data
        except FileNotFoundError:
            print(f'Error: the file {self.customer_csv} was not found')
            return None
        except pd.errors.EmptyDataError:
            print(f'Error: the file {self.customer_csv} is empty')
            return None
        except pd.errors.ParserError as e:
            print(f'Error: An error occured while parsing the file {self.customer_csv} : {e}')
            return None
        except Exception as e:
            print(f'An expected error occred: {e}')
            return None
    
    #Load to database
    def load_customer_to_database(self, engine, table_name_customer):
        if self.customer_data is not None:
            count_data = self.customer_data.shape[0]
            with engine.connect() as connection:
                self.customer_data.to_sql(name=table_name_customer, con= connection, index=False, if_exist='replace')
                print(f'Total Record has been inserted are {count_data} to table {table_name_customer} ')
        else:
            print(f'No data available to load. Please read the CSV first')
        return

class RetailDataProduct:
    def __init__(self, product_csv):
        self.product_csv = product_csv
        self.product_data = None
        
    def read_product_csv(self):
        try:
            key_columns = ['product_id', 'customer_id']
            all_files = glob.glob(product_csv)
            all_data = pd.concat([pd.read_csv(file) for file in all_files], ignore_index=True)
            # Mengganti koma dengan spasi di kolom 'description'
            all_data['description'] = all_data['description'].str.replace(",", " ")
            # Mengubah format tanggal
            all_data['invoice_date'] = pd.to_datetime(all_data['invoice_date'], format='%m/%d/%Y %H:%M', errors='coerce')
            # Mengubah format tanggal menjadi yyyy-MM-dd
            all_data['invoice_date'] = all_data['invoice_date'].dt.strftime('%Y-%m-%d')
            # Menghapus baris dengan nilai NaN di kolom kunci
            self.product_data = all_data.dropna(subset=key_columns).copy()
            # Mengubah tipe data 'customer_id' menjadi integer
            self.product_data['customer_id'] = self.product_data['customer_id'].astype(int)
            return self.product_data
        except FileNotFoundError:
            print(f'Error: the file {self.product_csv} was not found')
            return None
        except pd.errors.EmptyDataError:
            print(f'Error: the file {self.product_csv} is empty')
            return None
        except pd.errors.ParserError as e:
            print(f'Error: An error occured while parsing the file {self.product_csv} : {e}')
            return None
        except Exception as e:
            print(f'An expected error occred: {e}')
            return None
    
    def cleaning_product_data(self):
        clean_product_replace = sqldf('''select * from self.product_data
                            where product_id != 'product_id' and product_id is not null
                            and replace(description, ',', ' ')''')
        # Sort data by product_id
        sort_data_retail_cleanup = clean_product_replace.sort_values(by=['product_id'], ascending=True)
        # Remove duplicates based on product_id
        dedup_data_retail_cleanup = sort_data_retail_cleanup.drop_duplicates(subset='product_id', keep='first').copy()  # Tambahkan .copy() di sini
        # Convert product_group to lowercase
        dedup_data_retail_cleanup.loc[:, 'product_group'] = dedup_data_retail_cleanup['product_group'].str.lower()  # Gunakan .loc[] di sini
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
        dedup_data_retail_cleanup.loc[:, 'location'] = dedup_data_retail_cleanup['product_group'].map(location_map).fillna('not register yet')  # Gunakan .loc[] di sini

        # Select the relevant columns
        #result_product = dedup_data_retail_cleanup[['product_id', 'product_group', 'location']]
        self.product_data = dedup_data_retail_cleanup[['product_group', 'location']].copy()
        self.product_data.loc[:, 'productID'] = range(1, len(self.product_data)+1)
        return self.product_data
        
    def load_product_to_database(self, engine, table_name_product):
        if self.product_data is not None:
            count_data_product = self.product_data.shape[0]
            with engine.connect() as connection:
                self.product_data.to_sql(name=table_name_product, con= connection, index=False, if_exist='replace')
                print(f'Total Record has been inserted are {count_data_product} to table {table_name_product} ')
        else:
            print(f'No data available to load. Please read the CSV first')
        
        return
        
    
        
# Konfigurasi database
customer_csv = './input/customer_info.csv'
product_csv = './input/product_*.csv'
db_uri = 'postgresql+psycopg2://postgres:12345@host.docker.internal:5432/airflow_data'
table_name_customer = 'customers'
table_name_product = 'products'
    #f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'

# Buat engine SQLAlchemy
engine = create_engine(db_uri)
#class customer
retail_data_customer = RetailDataCustomer(customer_csv)
retail_data_customer.read_customer_csv()
retail_data_customer.load_customer_to_database(engine, table_name_customer)  # Load data to the database

#class product
retail_data_product = RetailDataProduct(product_csv)
retail_data_product.read_product_csv()
retail_data_product.load_product_to_database(engine, table_name_product)

import pandas as pd
import numpy as np
from pandasql import sqldf
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import calendar
import glob

#table customer
def tb_customer(csv_customer):
    customer_rd = pd.read_csv(csv_customer, skip_blank_lines=True)
    
    customer_rd = customer_rd.loc[:, ~customer_rd.columns.str.contains('^Unnamed')]
    
    filtered_customer = customer_rd[customer_rd['phone'].notnull()]
    
    return filtered_customer


# Fungsi untuk membaca semua data dari file CSV yang sesuai pola
def read_all_product_data(csv_transaction_pattern):
    key_columns = ['product_id', 'customer_id']
    
    # Menggunakan glob untuk mendapatkan semua file yang sesuai dengan pola
    all_files = glob.glob(csv_transaction_pattern)
    
    # Membaca dan menggabungkan semua file CSV ke dalam satu DataFrame
    all_data = pd.concat([pd.read_csv(file) for file in all_files], ignore_index=True)
    
    # Mengganti koma dengan spasi di kolom 'description'
    all_data['description'] = all_data['description'].str.replace(",", " ")
    
    # Mengubah format tanggal
    all_data['invoice_date'] = pd.to_datetime(all_data['invoice_date'], format='%m/%d/%Y %H:%M', errors='coerce')
    
    # Mengubah format tanggal menjadi yyyy-MM-dd
    all_data['invoice_date'] = all_data['invoice_date'].dt.strftime('%Y-%m-%d')
    
    # Menghapus baris dengan nilai NaN di kolom kunci
    clean_all_data = all_data.dropna(subset=key_columns).copy()
    
    # Mengubah tipe data 'customer_id' menjadi integer
    clean_all_data['customer_id'] = clean_all_data['customer_id'].astype(int)
    
    return clean_all_data


#mapping data for table product
def product_table(clean_all_data):
    #key_columns = ['product_id', 'product_name', 'location']
    # Sort data by product_id
    sort_data_retail_cleanup = clean_all_data.sort_values(by=['product_id'], ascending=True)
    
    # Remove duplicates based on product_id
    dedup_data_retail_cleanup = sort_data_retail_cleanup.drop_duplicates(subset='product_name', keep='first').copy()  # Tambahkan .copy() di sini
    
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
    #result_product = sort_data_retail_cleanup.drop_duplicates(subset = key_columns, keep='first')
    result_product = dedup_data_retail_cleanup[['product_name', 'location']].copy()
    result_product.loc[:, 'productID'] = range(1, len(result_product)+1)
    
    
    return result_product


#join data
def join_data(data_customer, transaction_data):
    df_join_data = sqldf('''select 
                            tr.customer_id,
                            c.customer_name,
                            c.email_address as email,
                            c.country, c.phone,
                            tr.product_id,
                            tr.invoice_no,
                            tr.stock_code,
                            tr.description,
                            tr.invoice_date,
                            tr.quantity,
                            tr.unit_price as price,
                            tr.product_group,
                            tr.product_name,
                            tr.stock 
                            from transaction_data tr
                            join data_customer c on tr.customer_id = c.customer_id
                            where tr.quantity > 0''',locals())
    
    return df_join_data


#create table orders
def tb_orders(all_data_join):
    amount_per_unit = (all_data_join['quantity'] * all_data_join['price']).round(2)
    
    #menambahkan amount ke Dataframe
    all_data_join['amount_per_unit'] = amount_per_unit
    
    orders = all_data_join[['customer_id','invoice_date', 'invoice_no', 'amount_per_unit']]
    
    # Mengelompokkan data berdasarkan 'invoice_number' dan 'invoice_date'
    # Lalu menjumlahkan 'amount_per_unit' untuk setiap grup
    total_amount_per_invoice = orders.groupby(['customer_id','invoice_no', 'invoice_date'])['amount_per_unit'].sum().reset_index()
    
    total_amount_per_invoice.loc[:, 'order_id'] = range(1, len(total_amount_per_invoice)+1)
    
    return total_amount_per_invoice



csv_customer = './input/customer_info.csv'
csv_transaction_pattern = './input/product_*.csv'

#call table customer
table_customer = tb_customer(csv_customer)

#call table transaction
table_transaction = read_all_product_data(csv_transaction_pattern)

#generate table product
table_product = product_table(table_transaction)

#join table customer and product
df_join_customer_product = join_data(table_customer, table_transaction)

#generate table orders
table_orders = tb_orders(df_join_customer_product)
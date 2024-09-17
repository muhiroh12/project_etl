import pandas as pd
import glob
import sqlalchemy

class CSVReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_csv_file(self):
        try:
            # Use pd.read_csv with skip_blank_lines=True to skip blank lines in the CSV file
            df = pd.read_csv(self.file_path, skip_blank_lines=True)
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None

class DataCleaner:
    def __init__(self, df):
        self.df = df

    def clean_product_data(self):
        # Break down the cleaning process into smaller methods
        self.df = self.remove_unnamed_columns()
        self.df = self.convert_date_columns()
        self.df = self.remove_null_rows()
        return self.df

    def remove_unnamed_columns(self):
        # Remove unnamed columns
        return self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]

    def convert_date_columns(self):
        # Use pd.to_datetime to convert date columns to datetime format
        date_columns = ['date_column1', 'date_column2']
        for column in date_columns:
            self.df[column] = pd.to_datetime(self.df[column])
        return self.df

    def remove_null_rows(self):
        # Remove rows with null values
        return self.df.dropna()

class DatabaseLoader:
    def __init__(self, engine, table_name):
        self.engine = engine
        self.table_name = table_name

    def load_product_to_database(self, df):
        try:
            # Use with statement to ensure that database connections are closed
            with self.engine.connect() as connection:
                # Use if_exists='replace' instead of if_exist='replace'
                df.to_sql(name=self.table_name, con=connection, index=False, if_exists='replace')
        except Exception as e:
            print(f"Error loading data to database: {e}")

def main():
    # Find all CSV files matching a pattern
    csv_files = glob.glob('data/*.csv')
    
    # Check if the files are actually readable and contain the expected data
    for file in csv_files:
        csv_reader = CSVReader(file)
        df = csv_reader.read_csv_file()
        if df is not None:
            data_cleaner = DataCleaner(df)
            df = data_cleaner.clean_product_data()
            engine = sqlalchemy.create_engine('database_connection_string')
            database_loader = DatabaseLoader(engine, 'table_name')
            database_loader.load_product_to_database(df)

if __name__ == "__main__":
    main()
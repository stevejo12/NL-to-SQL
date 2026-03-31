import os
import pandas as pd

# Configuration
data_folder = 'Data'
output_sql_file = 'db_creation_eurostat.sql'
database_name = 'eurostat_econ'

TARGET_COL = 'geo: Geopolitical entity (reporting)'

def generate_sql():
    sql_statements = [f"CREATE DATABASE IF NOT EXISTS {database_name};\n", f"USE {database_name};\n"]
    
    # Iterate through all CSV files in the folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.csv'):
            table_name = os.path.splitext(filename)[0]
            file_path = os.path.join(data_folder, filename)
            
            # Use pandas to infer data types
            df_headers = pd.read_csv(file_path, nrows=10)
            columns_list = df_headers.columns.to_list()
            
            # Start Building CREATE TABLE
            create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            col_defenitions = []
            
            for col_name, dtype in df_headers.dtypes.items():
                if col_name == TARGET_COL:
                    col_defenitions.append(f"    `geo` VARCHAR(9)")
                    col_defenitions.append(f"    `geopolitical_entity` VARCHAR(255)")
                else:
                # Map pandas types to MySQL types
                    if "int" in str(dtype):
                        sql_type = "INT"
                    elif "float" in str(dtype):
                        sql_type = "FLOAT"
                    elif "datetime" in str(dtype):
                        sql_type = "DATETIME"
                    else:
                        sql_type = "VARCHAR(255)"

                    col_defenitions.append(f"    `{col_name}` {sql_type}")
            
            create_stmt += ",\n".join(col_defenitions) + "\n);\n"
            sql_statements.append(create_stmt)
            
            # Build the LOAD DATA statement with variables (@)
            # We map columns to variables so we can manipulate them in the SET clause
            load_columns = []
            for col in columns_list:
                if col == TARGET_COL:
                    load_columns.append("@messy_geo")
                else:
                    load_columns.append(f"`{col}`")

            load_stmt = (
                # f"LOAD DATA LOCAL INFILE '{os.path.abspath(file_path)}'\n"
                f"LOAD DATA LOCAL INFILE '/var/lib/mysql-files/{os.path.basename(file_path)}'\n"
                f"INTO TABLE {table_name}\n"
                f"FIELDS TERMINATED BY ','\n"
                f"ENCLOSED BY '\"'\n"
                f"LINES TERMINATED BY '\\n'\n"
                f"IGNORE 1 ROWS\n"
                f"({', '.join(load_columns)})"
            )
            
            # Add the SET logic if the target column was found
            if TARGET_COL in columns_list:
                load_stmt += (
                    "\nSET \n"
                    "    `geo` = SUBSTRING_INDEX(@messy_geo, ': ', 1),\n"
                    "    `geopolitical_entity` = SUBSTRING_INDEX(@messy_geo, ': ', -1);"
                )
            else:
                load_stmt += ";"
                
            sql_statements.append(load_stmt)
            print(f"Processed: {filename} (Split applied: {TARGET_COL in columns_list})")

    # Write to the .sql file
    with open(output_sql_file, 'w') as f:
        f.write("\n".join(sql_statements))
    
    print(f"\nSuccess! SQL script saved to: {output_sql_file}")

if __name__ == "__main__":
    generate_sql()
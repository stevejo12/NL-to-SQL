import os
import pandas as pd

#Todo: double column logic (detection and columns to drop),
#  create region type column, 
# dates to keep, 
# logic for isced11 column, 
# automatic database creation


# Configuration
data_folder = 'Data'
output_sql_file = 'db_creation_eurostat.sql'
database_name = 'eurostat_econ'

SPECIAL_COLUMN_A = 'isced11: International Standard Classification of Education (ISCED 2011)'
SPECIAL_COLUMN_B = 'geo: Geopolitical entity (reporting)'

columns_to_drop = {
    'Unit of measure',
    'sectperf',
    'STRUCTURE', 
    'STRUCTURE_ID',
    'STRUCTURE_NAME', 
    'freq: Time frequency',
    'freq',
    'Time frequency', 
    'CONF_STATUS',
    'Confidentiality status (flag)',
    'CONF_STATUS: Confidentiality status (flag)',
    'OBS_FLAG',
    'Observation status (Flag) V2 structure',
    'OBS_FLAG: Observation status (Flag) V2 structure',
}

geo_mapping = {
    2: "Country",
    3: "NUTS 1",
    4: "NUTS 2",
    5: "NUTS 3"
}

TABLE_NAMES = {
    "GDP_at_current_market_prices_by_NUTS_2_region.csv": "GDP",
    "GERD_by_sector_of_performance_and_NUTS_2_region.csv": "GERD",
    "Employed_persons_by_NUTS_2_region.csv": "Employed",
    "Unemployed_persons_by_educational_attainment_level_and_NUTS_2_region.csv": "Unemployed",
    "Employed_persons_by_educational_attainment_level_and_NUTS_2_region.csv": "Employed_by_Education",
    "Population_in_private_households_by_educational_attainment_level_and_NUTS_2_region.csv": "Population_by_Education",
}

def generate_sql() -> bool:
    sql_statements = [f"CREATE DATABASE IF NOT EXISTS {database_name};\n", f"USE {database_name};\n"]
    
    # Iterate through all CSV files in the folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.csv'):
            # table_name = os.path.splitext(filename)[0]
            # file_path = os.path.join(data_folder, filename)
            table_name = TABLE_NAMES.get(filename, os.path.splitext(filename)[0])
            file_path = os.path.join(data_folder, filename)
            
            # Use pandas to infer data types
            df_headers = pd.read_csv(file_path, nrows=10)
            original_columns = df_headers.columns.to_list()
            ##Split all columns with ': ' in the header, and remove the 2nd of those two columns, 
            ##unless certain rules apply. 
            cols_to_split_s = {col for col in original_columns if ': ' in col}
            for col in original_columns:
                if col in cols_to_split_s:
                    name1, name2 = col.split(': ')
                    split_cols = df_headers[col].astype(str).str.split(': ', expand=True, n=1)
                    if split_cols.shape[1] == 1:
                        split_cols[1] = None
                    df_headers[[name1, name2]] = split_cols
                    df_headers = df_headers.drop(columns=[col])
                    if col == SPECIAL_COLUMN_A:
                        columns_to_drop.add(name1)
                    elif col == SPECIAL_COLUMN_B:
                        pass
                    else:
                        columns_to_drop.add(name2)
            
            # Start Building CREATE TABLE
            create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            col_defenitions = []
            df_headers = df_headers.drop(columns_to_drop, axis=1, errors='ignore')
            for col_name, dtype in df_headers.dtypes.items():
                # Map pandas types to MySQL types
                    if col_name == 'geo':
                        # sql_type = "VARCHAR(10) PRIMARY KEY"
                        sql_type = "VARCHAR(10)"
                    elif "int" in str(dtype):
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
            for col in original_columns:
                if col in columns_to_drop:
                    name = '@dummy'
                    load_columns.append(f"{name}")
                elif col in cols_to_split_s:
                    clean_var = col.replace(': ', '_').replace(' ', '_').replace('(', '').replace(')', '')
                    if col == SPECIAL_COLUMN_A:
                        clean_var = "isced11"
                    name = f"@messy_{clean_var}"
                    load_columns.append(name)
                else:
                    load_columns.append(f"`{col}`")

            load_stmt = (
                # f"LOAD DATA LOCAL INFILE '{os.path.abspath(file_path)}'\n"
                f"LOAD DATA LOCAL INFILE '{data_folder}/{os.path.basename(file_path)}'\n"
                f"INTO TABLE {table_name}\n"
                f"FIELDS TERMINATED BY ','\n"
                f"ENCLOSED BY '\"'\n"
                f"LINES TERMINATED BY '\\n'\n"
                f"IGNORE 1 ROWS\n"
                f"({', '.join(load_columns)})\n"
            )

            set_assignments = []
            YEAR_MIN = 2019
            YEAR_MAX = 2024
            filter_timeperiod = (
                f"DELETE FROM {table_name} WHERE TIME_PERIOD < {YEAR_MIN} OR TIME_PERIOD > {YEAR_MAX};"
            )
            # Add the SET logic if the target column was found
            if SPECIAL_COLUMN_B in original_columns:
                set_assignments.append("    `geo` = SUBSTRING_INDEX(@messy_geo, ': ', 1)")
                set_assignments.append("    `Geopolitical entity (reporting)` = SUBSTRING_INDEX(@messy_geo, ': ', -1)")
                cols_to_split_s.remove(SPECIAL_COLUMN_B)
            if SPECIAL_COLUMN_A in original_columns:
                set_assignments.append("    `International Standard Classification of Education (ISCED 2011)` = SUBSTRING_INDEX(@messy_isced11, ': ', -1)")
                cols_to_split_s.remove(SPECIAL_COLUMN_A)

            for col in list(cols_to_split_s):
              if col in original_columns:
                clean_var = col.replace(': ', '_').replace(' ', '_').replace('(', '').replace(')', '')
                source_name = f"@messy_{clean_var}"
                dest_name = col.split(': ')[0]
                temp_load_stmt += f"    `{dest_name}` = SUBSTRING_INDEX({source_name}, ': ', 1),\n"
            
            if set_assignments:
                load_stmt += "\nSET\n" + ",\n".join(set_assignments)

            load_stmt += ";\n"
            sql_statements.append(load_stmt)

            sql_statements.append(f"ALTER TABLE {table_name} ADD region_type VARCHAR(10);\n")

            sql_statements.append(
                    f"UPDATE {table_name} SET"
                    f"    `region_type` = CASE \n"
                    f"        WHEN CHAR_LENGTH(`geo`) = 2 THEN 'Country'\n"
                    f"        WHEN CHAR_LENGTH(`geo`) = 3 THEN 'NUTS 1'\n"
                    f"        WHEN CHAR_LENGTH(`geo`) = 4 THEN 'NUTS 2'\n"
                    f"        WHEN CHAR_LENGTH(`geo`) = 5 THEN 'NUTS 3'\n"
                    f"        ELSE 'Other'\n"
                    f"END;\n"
                )
            
            sql_statements.append(filter_timeperiod)
            print(f"Processed: {filename}")

    # Write to the .sql file
    with open(output_sql_file, 'w') as f:
        f.write("\n".join(sql_statements))
    
    print(f"\nSuccess! SQL script saved to: {output_sql_file}")
    return True

if __name__ == "__main__":
    generate_sql()
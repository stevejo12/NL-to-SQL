import streamlit as st
from helpers.langchain import get_few_shot_db_chain
from helpers.visual import extract_sql_query, extract_sql_result, infer_column_names
import pandas as pd
import os
import mysql.connector
from sqlMaker import generate_sql
from dotenv import load_dotenv

load_dotenv()

def run_sql_file(filename, config):
    """
    Execute a .sql file command by command.
    Splits on ';\\n' to avoid breaking multi-line statements.
    """
    try:
        db = mysql.connector.connect(**config, allow_local_infile=True)
        cursor = db.cursor()

        with open(filename, 'r', encoding='utf-8') as f:
            sql_file = f.read()

        # Split on semicolon followed by newline
        commands = sql_file.split(';\n')

        print(f"Executing {filename} command by command...")

        for i, command in enumerate(commands):
            clean_command = command.strip()

            if not clean_command:
                continue

            try:
                cursor.execute(clean_command)
                db.commit()
            except mysql.connector.Error as cmd_err:
                print(f"Error in command #{i}: {clean_command[:80]}...")
                print(f"Reason: {cmd_err}\n")

        print(f"Successfully executed {filename}")
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

SQL_DUMP_FILE = "db_creation_eurostat.sql"

DB_CONFIG = {
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
}

def ensure_database_ready():
    generate_sql()
    return True

def initialize():
    cooked = ensure_database_ready()
    if cooked:
        run_sql_file(SQL_DUMP_FILE, DB_CONFIG)

if "initialized" not in st.session_state:
    initialize()
    st.session_state.initialized = True

st.title("Database Q&A using LangChain")
question =st.text_input("Question: ")
if question:
    chain=get_few_shot_db_chain()
    response = chain.invoke({"query": question})

    st.header("Answer:")
    st.write(response.get("result"))

    #visuals
    try:
        sql_result = extract_sql_result(response)
        sql_query = extract_sql_query(response)

        if sql_query:
            with st.expander("Generated SQL"):
                st.code(sql_query, language="sql")

        if sql_result:
            n_cols = len(sql_result[0]) if sql_result and isinstance(sql_result[0], (tuple, list)) else 1
            col_names = infer_column_names(sql_query, n_cols)
            df = pd.DataFrame(sql_result, columns=col_names)

        if not df.empty:
            st.header("Data Table:")
            st.dataframe(df)

            # Chart: need at least one numeric column beyond the first
            numeric_cols = [c for c in df.columns[1:] if pd.api.types.is_numeric_dtype(df[c])]
            if len(df) > 1 and numeric_cols:
                st.header("Visual Analysis:")
                st.bar_chart(df, x=df.columns[0], y=numeric_cols[0])
    except Exception as e:
        st.info(f"Error parsing table: {e}")

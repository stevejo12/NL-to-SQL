import streamlit as st
from langchain_helper import get_few_shot_db_chain
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
    sql_result=None
    steps = response.get("intermediate_steps", [])
    for step in steps:
      if isinstance(step, dict) and "sql_result" in step:
        sql_result = step["sql_result"]
        break
      # If it's the raw list of tuples/decimals
      elif isinstance(step, list):
        sql_result = step
        break
      # If it's a string representation, we need to handle the 'Decimal' type
      elif isinstance(step, str) and "[" in step:
        from decimal import Decimal
        # eval() needs Decimal in the namespace to understand the SQLResult string
        sql_result = eval(step)
        break
    
    if sql_result:
      st.header("Data Table:")
      df = pd.DataFrame(sql_result)
      if not df.empty:
        st.dataframe(df)
        
        if len(df.columns) >= 2:
          st.header("Visual Analysis:")
          st.bar_chart(data=df, x=df.columns[0].astype(str), y=df.columns[1].astype(str))
  except Exception as e:
    st.info(f"Error  parsing table: {e}")

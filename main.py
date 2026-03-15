import streamlit as st
from langchain_helper import get_few_shot_db_chain
import pandas as pd
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

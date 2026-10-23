from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from helpers.qdrant_store import build_qdrant_store
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
load_dotenv()
from few_shots import few_shots

def get_few_shot_db_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.2
    )

    load_dotenv()
    db_user = os.getenv("DATABASE_USER")
    db_password = os.getenv("DATABASE_PASSWORD")  # safely encodes special characters
    db_host = os.getenv("DATABASE_HOST")
    db_name = os.getenv("DATABASE_NAME")

    db = SQLDatabase.from_uri(
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
        sample_rows_in_table_info=3
    )
    embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.environ["GOOGLE_API_KEY"])

    to_vectorize = [" ".join(example.values()) for example in few_shots]
    vectorstore = build_qdrant_store(to_vectorize, embeddings, few_shots)
    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore,
        k=3,
    )
    
    example_prompt = PromptTemplate(
        input_variables=["Question", "SQLQuery", "SQLResult","Answer",],
        template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
    )

    mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Pay attention to use CURDATE() function to get the current date, if the question involves "today".

    IMPORTANT NOTES FOR THE Population_by_Education TABLE:
    - This table contains CUMULATIVE ISCED education categories, not disjoint ones.
    - The row 'Tertiary education (levels 5-8)' DOES NOT EXIST in this table.
    - To compute tertiary share, you MUST derive it as:
        (levels 3-8) MINUS (levels 3 and 4)
        using a self-join on Population_by_Education.
    - See the example questions below for the exact pattern.
    
    Use the following format:
    
    Question: Question here
    SQLQuery: Query to run with no pre-amble
    SQLResult: Result of the SQLQuery
    Answer: Final answer here
    
    No pre-amble.
    """

    prompt_suffix= """
    Only use the following tables:
    {table_info}

    Question: {input}
    """
    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=mysql_prompt,
        suffix=prompt_suffix,
        input_variables=["input", "table_info", "top_k"] #These variables are used in the prefix and suffix
    )

    chain = SQLDatabaseChain.from_llm(
        llm,
        db, 
        verbose=True, 
        prompt=few_shot_prompt,
        return_intermediate_steps=True
    )

    return chain


if __name__=='__main__':
    chain=get_few_shot_db_chain()
    print(chain.run("How many white color Levi's shirt I have?"))
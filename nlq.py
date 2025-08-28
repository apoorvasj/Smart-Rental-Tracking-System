"""
Natural language query the Postgres database (FastAPI + LangChain + Groq).
"""
import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate

load_dotenv()
DB_URI = os.getenv("DB_URI")

# SQLDatabase wraps the DB schema for LangChain
db = SQLDatabase.from_uri(DB_URI)

# LLM (make sure your environment has required creds for langchain_groq)
llm = ChatGroq(model="llama-3.1-8b-instant")

# System prompt + human prompt — IMPORTANT: use {query} placeholder
system_prompt = """
You are a SQL expert. Convert user natural language into valid SQL queries
for a PostgreSQL database.

Rules:
1. Always use explicit, absolute dates when the user mentions months/years.
   Example: "past April 2025" -> "AND check_out_date > '2025-04-01'".
2. Only use CURRENT_DATE or relative intervals if the user explicitly says
   'today', 'yesterday', 'last 7 days', or 'past month'.
3. Always return a clean, executable SQL query (the chain should execute it
   and return the final result when possible).
   
Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:

{table_info}


Question: {input}
"""

PROMPT =  PromptTemplate(
    input_variables = ["input","table_info", "dialect"], template = system_prompt)


# Build the chain. return_direct=True asks the chain to execute SQL and return final result.
db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=PROMPT, verbose=True,
                                     return_direct=True)

# ---------- FastAPI ----------
app = FastAPI(title="RAG SQL Chatbot API")


@app.post("/chat")
def chat(query):
    """
    Accepts JSON: {"question": "How many vehicles are active past April 2025?"}
    Returns JSON: {"answer": ...}
    """
    try:
      
        # Modified to use run() instead of invoke()
        res = db_chain.run(query)
        logging.info("raw chain response: %s", res)

        # Simplify the response handling
        print('Printing response')
        print(str(res))
        return {"answer": str(res)}

    except Exception as e:
        logging.exception("error running chain")
        return {"error": str(e)}

import streamlit as st
import pandas as pd
import sqlite3
from sqlite3 import Error
import os
from dotenv import load_dotenv
import requests
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from gpt_utils import *
from prompt import *

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -------------------- Database Functions --------------------

# Function to create a SQLite database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        st.success(f"Connected to SQLite Database: {db_file}")
    except Error as e:
        st.error(f"Error connecting to database: {e}")
    return conn

# Function to create a table from dataframe
def create_table_from_df(conn, df, table_name):
    try:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        st.success(f"Data successfully stored in table '{table_name}'")
    except Error as e:
        st.error(f"Error storing data in table: {e}")

# Function to ensure the csv_tables table exists for storing CSV table names
def create_csv_table_list(conn):
    try:
        query = """
        CREATE TABLE IF NOT EXISTS csv_tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT UNIQUE NOT NULL
        );
        """
        conn.execute(query)
    except Error as e:
        st.error(f"Error creating 'csv_tables' table: {e}")

# Function to insert table name into the csv_tables table
def store_table_name(conn, table_name):
    try:
        query = "INSERT OR IGNORE INTO csv_tables (table_name) VALUES (?);"
        conn.execute(query, (table_name,))
        conn.commit()
        st.success(f"Table name '{table_name}' stored in 'csv_tables' cluster")
    except Error as e:
        st.error(f"Error storing table name: {e}")

# Function to fetch all CSV table names from the cluster
def get_csv_tables(conn):
    try:
        query = "SELECT table_name FROM csv_tables;"
        tables = pd.read_sql(query, conn)
        return tables['table_name'].tolist()
    except Error as e:
        st.error(f"Error fetching CSV table names: {e}")
        return []

# Function to clean dataframe column names
def clean_column_names(df):
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace(':', '_')
    return df

# Function to fetch the content of a table from the database
def fetch_table_data(conn, table_name):
    try:
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, conn)
        return df
    except Error as e:
        st.error(f"Error fetching data from table '{table_name}': {e}")
        return pd.DataFrame()

# -------------------- Streamlit Application --------------------

# Set the title of the application
st.title("Multi AI NL2SQL Agent")

# Step 1: Input for database name
if "csv_db_name" not in st.session_state:
    st.session_state.csv_db_name = 'Uploaded_csv.sqlite'

with st.sidebar:
    # Create SQLite database connection
    if "conn" is not None:
        conn = create_connection(st.session_state.csv_db_name)
        st.session_state.conn = conn

    # File uploader for CSV
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None and "upload" not in st.session_state:
        try:
            # Try reading with UTF-8 encoding
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            st.warning("UTF-8 decoding failed. Retrying with ISO-8859-1 encoding.")
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')

        # Clean the column names of the dataframe
        df = clean_column_names(df)
        st.write("Preview of the uploaded CSV:")
        st.write(df.head())

        # Extract table name from the uploaded file name (without the extension)
        csv_filename = uploaded_file.name
        table_name = 'csv_data'

        if table_name:
            if conn is not None:
                # Ensure the csv_tables cluster table exists
                create_csv_table_list(conn)

                # Store CSV data into the database
                create_table_from_df(conn, df, table_name)

                # Store the table name in csv_tables cluster
                store_table_name(conn, table_name)

                # Display the list of tables in csv_tables cluster
                csv_tables = get_csv_tables(conn)
                st.success("Task Completed")

    if conn:
        conn.close()

# -------------------- Agent Initialization --------------------

# Initialize tools and agent
if "csv_tool" not in st.session_state:
    st.session_state.csv_tool = csv_tool()

if "sql_tool" not in st.session_state:
    st.session_state.sql_tool = sql_tool()

if "prompt" not in st.session_state:
    st.session_state.prompt = get_prompt()

if "agent_executor" not in st.session_state:
    llm = ChatOpenAI(api_key=OPENAI_API_KEY)
    agent = create_openai_tools_agent(llm, [st.session_state.csv_tool, st.session_state.sql_tool], st.session_state.prompt)
    st.session_state.agent_executor = AgentExecutor(agent=agent, tools=[st.session_state.csv_tool, st.session_state.sql_tool], verbose=True, handle_parsing_errors=True, max_iterations=5)

# -------------------- Chat UI --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process new query input
if query := st.chat_input("Enter your query:"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Generating response..."):
        messages = st.session_state.messages
        messages_str = "".join([f"{message['role'].capitalize()}: {message['content']}///" for message in messages])

        result = st.session_state.agent_executor.invoke({"input": query})
        st.markdown(result['output'])

        st.session_state.messages.append({"role": "assistant", "content": result['output']})

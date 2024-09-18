from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
import google.generativeai as genai
import sqlite3
import logging
import re
# Initialize FastAPI app
# app = FastAPI()
logger = logging.getLogger(__name__)
# router = APIRouter()
router = APIRouter()

# Google Generative AI configuration
genai.configure(api_key='AIzaSyDKJg86Nh4-mlCl6LU8am2Cv8yXHcFWZm4')

# Set up the generative model
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# SQL query function
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

# Get column names from the table
def get_column_names(db, table_name):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        
        # Get column names from the specified table
        cur.execute(f"PRAGMA table_info({table_name})")
        columns_info = cur.fetchall()
        print("extracted")
        print(columns_info)
        columns = [col[1] for col in columns_info]  # The second item in each row is the column name
        
        if not columns:
            raise Exception("Table has no columns or doesn't exist.")
        
        return columns
    except sqlite3.Error as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

# Fetch sample records from the table
def get_sample_records(db, table_name, limit=1):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        # Get some sample records
        cur.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        sample_records = cur.fetchall()

        return sample_records
    except sqlite3.Error as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

remove_code_block_syntax = lambda text: re.sub(r"```(sql|)\s*(.*?)\s*```", r"\2", text, flags=re.DOTALL)

# Request model for FastAPI
class QueryRequest(BaseModel):
    question: str

@router.post("/chat-with-csv")
async def chat_with_csv(query_request: QueryRequest):
    table_name = 'csv_data'
    question = query_request.question
    db_path = "uploaded_csv.sqlite"  # Fixed SQLite database name
    
    # Fetch column names from the table
    columns = get_column_names(db_path, table_name)
    print(columns)
    if "error" in columns:
        raise HTTPException(status_code=400, detail=columns["error"])
    
    # Fetch sample records from the table
    sample_records = get_sample_records(db_path, table_name)
    print("\n\n\nsample Records")
    print(sample_records)
    if "error" in sample_records:
        raise HTTPException(status_code=400, detail=sample_records["error"])

    # Format sample records as strings
    sample_records_str = '\n'.join([str(record) for record in sample_records])

    # Create the input prompt for the model with sample records
    input_prompt = (f"You are an expert in converting English questions to SQL code! "
                    f"The SQL database has a table named {table_name} with the following columns: "
                    f"{', '.join(columns)}.\n\n"
                    f"Here are some sample records from the table:\n"
                    f"{sample_records_str}\n\n"
                    f"For example, Example 1 - How many entries of Adidas are present?, the SQL command will be something like this:\n"
                    "`SELECT COUNT(*) FROM fashion_products WHERE brand = 'Adidas';`\n\n"
                    "The above examples are just for your understanding on how to generate SQL queries, they are not dependent on my table or database. "
                    "Note you are supposed to give me only the SQL query and nothing else. You are mostly adding something at beginning "
                    "which is causing me errors. You are giving out errors with some phrases at the beginning or ending. "
                    "Make sure not to repeat it. See the example queries how they are generated but strictly don't follow them; they are just examples.")

    # Combine input prompt and user question
    prompt_parts = [input_prompt, question]
    
    # Generate SQL query from the question
    response = model.generate_content(prompt_parts)

    clean_sql_query = remove_code_block_syntax(response.text)
    
    # Execute the generated SQL query
    query_result = read_sql_query(clean_sql_query, db_path)
    
    return {"sql_query": clean_sql_query, "result": query_result}

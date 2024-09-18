from fastapi import FastAPI,APIRouter,HTTPException
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

# Route to process the question and generate SQL query
@router.post("/query")
async def generate_gemini_response(query_request: QueryRequest):
    question = query_request.question
    sample_records = get_sample_records("health.sqlite", "healthcare_dataset")
    print("\n\n\nsample Records")
    print(sample_records)
    if "error" in sample_records:
        raise HTTPException(status_code=400, detail=sample_records["error"])

    sample_records_str='\n'.join([str(record) for record in sample_records])
    input_prompt = ("You are an expert in converting English questions to SQL code! "
                    "The SQL database has my table with name healthcare_dataset and has the following columns - "
                    "Name, Age, Gender, Blood_Type, Medical_Condition, Date_of_Admission, Doctor, Hospital, "
                    "Insurance_Provider, Billing_Amount, Room_Number, Admission_Type, Discharge_Date, Medication, Test_Results.\n\n"
                    "Here are some sample records from the table:\n"
                    f"{sample_records_str}\n\n"
                    "For example, Example 1 - How many entries of Adidas are present?, the SQL command will be something like this\n"
                    "`SELECT COUNT(*) FROM fashion_products WHERE brand = 'Adidas';`\n\n"
                    "Example 2 - How many XL products of Nike are there that have a rating of more than 4?\n"
                    "`SELECT COUNT(*) FROM fashion_products WHERE brand = 'Nike' AND size = 'XL' AND \"Rating\" > 4;`\n\n"
                    "Note you are supposed to give me only the SQL query and nothing else. You are giving out errors with some phrases at the beigining or ending. Make sure not to repeat it.")

    prompt_parts = [input_prompt, question]
    
    # Generate SQL query from the question
    response = model.generate_content(prompt_parts)

    clean_sql_query = remove_code_block_syntax(response.text)
    
    # Execute the SQL query and return the result
    query_result = read_sql_query(clean_sql_query, "health.sqlite")
    
    return {"sql_query": clean_sql_query, "result": query_result}


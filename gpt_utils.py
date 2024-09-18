from sql_wrapper import SQLQueryAPIWrapper
from csv_wrapper import CSVQueryAPIWrapper
from langchain.tools.base import StructuredTool

# -------------------- SQL Tool Initialization --------------------

def sql_tool():
    """
    This tool is responsible for converting English questions into SQL queries 
    and executing them on the 'healthcare_dataset' table stored in the SQL database.
    It analyzes the input query to determine if SQL operations are required 
    based on column references like 'Name', 'Age', 'Medical_Condition', 
    or common SQL operations such as SELECT, COUNT, WHERE.
    
    Description:
    - Ensures the output is purely SQL-based without extraneous phrases.
    - Targets predefined SQL databases.

    Returns:
    - StructuredTool for SQL operations.
    """
    web_search = SQLQueryAPIWrapper()
    web_tool = StructuredTool.from_function(
        name="SQL-Database-search",
        description=(
            "This tool converts English questions into SQL queries and executes "
            "them on the healthcare_dataset table stored in the SQL database. "
            "It identifies references to table columns such as 'Name', 'Age', "
            "'Medical_Condition', or common SQL operations like SELECT, COUNT, "
            "and WHERE. Only the SQL query is returned, ensuring no unnecessary phrases."
        ),
        func=web_search.run
    )
    return web_tool

# -------------------- CSV Tool Initialization --------------------

def csv_tool():
    """
    This tool handles queries related to CSV data stored in an SQL database.
    It is invoked when queries involve operations like searching or extracting 
    information from CSV-formatted data, even though the data is stored in SQL.
    
    Description:
    - Detects and manages queries related to CSV structures (rows, columns, etc.).
    - Retrieves relevant data from the SQL database based on CSV-related queries.

    Returns:
    - StructuredTool for CSV operations.
    """
    pdf_search = CSVQueryAPIWrapper()
    pdf_tool = StructuredTool.from_function(
        name="Search-in-uploaded-csv",
        description=(
            "This tool handles queries related to CSV data stored in the SQL database. "
            "It is invoked when the input query involves operations or searches related to CSV data. "
            "It automatically detects CSV-related queries and retrieves relevant data from the SQL database."
        ),
        func=pdf_search.run
    )
    return pdf_tool


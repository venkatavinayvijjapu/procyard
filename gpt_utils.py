from sql_wrapper import SQLQueryAPIWrapper
from csv_wrapper import CSVQueryAPIWrapper
# from langchain_community.utilities import GoogleSearchAPIWrapper
# from langchain_core.tools import Tool
from langchain.tools.base import StructuredTool


# def sql_tool():
#     web_search = SQLQueryAPIWrapper()
#     web_tool = StructuredTool.from_function(
#         name="SQL-Database-search",
#         description="Search in query",
#         func=web_search.run
#     )
#     return web_tool

def sql_tool():
    web_search = SQLQueryAPIWrapper()
    web_tool = StructuredTool.from_function(
        name="SQL-Database-search",
        description="This tool is responsible for converting English questions into SQL queries and executing them on the healthcare_dataset table stored in the SQL database. It automatically determines if a query should be executed in SQL by analyzing references to the table's columns, such as 'Name', 'Age', 'Medical_Condition', or common SQL operations (e.g., SELECT, COUNT, WHERE). The tool ensures that only the SQL query is returned, avoiding unnecessary phrases or errors in the output. This works on the predefined sql database",
        func=web_search.run
    )
    return web_tool


# def csv_tool():
#     pdf_search = CSVQueryAPIWrapper()
#     pdf_tool = StructuredTool.from_function(
#         name="Search-in-uploaded-csv",
#         description="Search in csv",
#         func=pdf_search.run
#     )
#     return pdf_tool


def csv_tool():
    pdf_search = CSVQueryAPIWrapper()
    pdf_tool = StructuredTool.from_function(
        name="Search-in-uploaded-csv",
        description="This tool is used to handle queries related to CSV data stored in the SQL database. It is invoked when the input query refers to operations or searches that involve extracting or interacting with CSV-formatted data, even though the data is stored in SQL. The tool automatically detects queries related to CSV structures (like rows, columns, or file-based operations) and retrieves the relevant data from the SQL database. This works on user's uploaded csv file.",
        func=pdf_search.run
    )
    return pdf_tool




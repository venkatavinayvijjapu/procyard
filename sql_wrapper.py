from typing import Any, Dict, Optional
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Extra
from langchain_core.tools import BaseTool
import requests

class SQLQueryAPIWrapper(BaseModel):
    """Wrapper for SQL Query API."""
    
    api_url: str = "http://127.0.0.1:8000"  # The API URL for your FastAPI app

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid

    def _sql_query(self, question: str) -> str:
        """Send the question to the FastAPI SQL query endpoint and return the response."""
        response = requests.post(f"{self.api_url}/query", json={"question": question})
        if response.status_code == 200:
            return response.json()  # Returning the full response which includes both SQL query and result
        else:
            return "Failed to fetch results"

    def run(self, query: str) -> str:
        """Run query through SQL API and parse result."""
        return self._sql_query(query)


class SQLQueryRun(BaseTool):
    """Tool that queries the SQL Query API."""

    name: str = "sql_query_tool"
    description: str = (
        "A wrapper around SQL Query API. "
        "Useful for converting natural language questions to SQL and getting results from the database. "
        "Input should be a natural language question."
    )
    api_wrapper: SQLQueryAPIWrapper

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool to query SQL API."""
        return self.api_wrapper.run(query)

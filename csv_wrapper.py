from typing import Optional
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Extra
from langchain_core.tools import BaseTool
import requests

class CSVQueryAPIWrapper(BaseModel):
    """Wrapper for CSV Query API."""
    
    api_url: str = "http://127.0.0.1:8000"  # The API URL for your FastAPI app

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid

    def _csv_query(self, question: str) -> dict:
        """Send the question to the FastAPI CSV query endpoint and return the response."""
        response = requests.post(f"{self.api_url}/chat-with-csv", json={"question": question})
        if response.status_code == 200:
            return response.json()  # Returning the full response which includes both SQL query and result
        else:
            return {"error": "Failed to fetch results"}

    def run(self, query: str) -> dict:
        """Run query through CSV Query API and parse result."""
        return self._csv_query(query)


class CSVQueryRun(BaseTool):
    """Tool that queries the CSV Query API."""

    name: str = "csv_query_tool"
    description: str = (
        "A wrapper around the CSV Query API. "
        "Useful for converting natural language questions to SQL and getting results from the CSV-based database. "
        "Input should be a natural language question."
    )
    api_wrapper: CSVQueryAPIWrapper

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool to query CSV API."""
        return self.api_wrapper.run(query)

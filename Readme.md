# Procureyard Assignment Overview

### Title
Text-to-SQL Query System with Multi-Source Data

### Task Brief
This project is a Streamlit-based multi-agent system designed to convert natural language queries into SQL and CSV operations. The system integrates various tools, including OpenAI, for generating queries and retrieving data from SQL databases and CSV files. It also supports query refinement and leverages conversation context for better interaction.

### Features

- **Natural Language to SQL**: Converts natural language questions into SQL queries and runs them on the database.
- **CSV Interaction**: Supports interaction with CSV data, stored in an SQL database, by interpreting queries related to CSV files.
- **Agent-Based System**: Uses a LangChain-based multi-agent architecture to determine which tool (SQL or CSV) should handle the query.


### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your OpenAI API key by creating a `.env` file:

    ```bash
    OPENAI_API_KEY=your-openai-api-key
    ```

## Usage

1. Start up the fastAPI server using Uvicorn
    ```bash
    uvicorn api:app --reload
    ```


2. Run the Streamlit application:

    ```bash
    streamlit run streamlit_app.py
    ```

3. Upload a CSV file and provide natural language queries. The system will decide whether to query the CSV or SQL database and return the appropriate result.

### Note:
- The health.sqlite if the fixed sql database and added in this mail.
- The csv file can uploaded as your choice, the csv will be stored in upload_csv.sqlite

### Challenges:
- Challenges faced are developing a prompt and getting data for that prompt.
- Other challenge is that the csv column are meant to have spaces in their csv names which created errors.
- While Gemini generated SQL queries it is adding some quotes at begging or ending so I have created a lambda function to structureize the sql query.
```bash
remove_code_block_syntax = lambda text: re.sub(r"```(sql|)\s*(.*?)\s*```", r"\2", text, flags=re.DOTALL)
```
### Video Prototype
You can look at the video prototype from [here](https://www.veed.io/view/d34173cd-2f9e-41dc-b275-394991ec12b4?panel=share)

from langchain import hub

# -------------------- Prompt Retrieval from Hub --------------------

def get_prompt():
    """
    Pulls the OpenAI tools agent prompt from the langchain hub.
    
    Returns:
    - A prompt object fetched from the hub repository.
    """
    prompt = hub.pull("hwchase17/openai-tools-agent")
    return prompt

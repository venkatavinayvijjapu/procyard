from langchain import hub
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
def get_prompt():
    prompt = hub.pull("hwchase17/openai-tools-agent")
    return prompt

# def get_main_prompt():
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", f"""
#     You are a helpful assistant. You are my Personal agent where  you need to work as Question and answering agent using uploaded Pdf or given URL or surf with internet. You are supposed to use the data shared with you, analyze it and answer my queries.
#     Additionally, efficiently utilize chat history to track the context and details of ongoing conversations. This enables you to handle follow-up questions more effectively, ensuring continuity and relevance in your interactions with users.
    
#     """),
#             MessagesPlaceholder("chat_history", optional=True),
#             # MessagesPlaceholder("user_id"),
#             ("human", "{input}"),
#             # MessagesPlaceholder("agent_scratchpad"),
#         ]
#     )
#     return prompt


def get_query_refiner_prompt(conversation_str, query):
    system_role = """Given the following user "Query" and "CONVERSATION LOG", formulate a "Refined Query" that would be the most relevant to provided "Query".  If no conversation log is available, set "Refined Query" same as the "Query" but in English . Please strictly ensure that the generated "Refined Query" is always in English. Ensure that the "Refined Query" is always in English."""
    example_text = f"""\n\nCONVERSATION LOG: \n

                        human: hi
                        ai: hi
                        human: What is Washing with hope??
                        ai: this is bot response

                        Query: What is its meaning?

                        """
    response_text = (
        "Refined Query: What is the meaning or significance behind Washing with hope?"
    )

    user_input = f"\n\nCONVERSATION LOG: \n{conversation_str}\n\nQuery: {query}\n\nRefined Query:"

    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": example_text},
        {"role": "assistant", "content": response_text},
        {"role": "user", "content": user_input},
    ]
    return messages
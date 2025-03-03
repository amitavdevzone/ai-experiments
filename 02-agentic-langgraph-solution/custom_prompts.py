from langchain.prompts import ChatPromptTemplate, ChatMessagePromptTemplate
from graph_state import GraphState
from utils import Utils

model = Utils.get_model()


def get_intent(state: GraphState):
    question = state["question"]
    system_template = """
    Classify the intent of this question into one of three categories:
    1. order
    2. product
    3. general
    Return only the intent category name.

    Example: 
    Where is my order? -> order
    When will I get my order delivered? -> order
    Can you recommend a good book? -> product
    What is the best book to read? -> product
    What is your name? -> general
    Who are you? -> general
    """
    system_message_prompt = ChatMessagePromptTemplate.from_template(
        role="system", template=system_template
    )

    human_message_prompt = ChatMessagePromptTemplate.from_template(
        role="user", template="Question from user: {question}"
    )

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    prompt = chat_prompt.format_messages(question=question)
    response = model.invoke(prompt)
    response = response.content.strip()
    state["user_intent"] = response
    return state

from typing import TypedDict, Union
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, Messages
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from memory import Memory

class State(TypedDict):
    messages: list
    memory: Memory

def generic_node(state: State) -> State:
    """Handle generic questions that do not fit into specific categories."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Respond to the user's questions in a friendly and informative manner.",
            ),
            ("human", "{input}"),
        ]
    )

    latest_message = state["messages"][-1].content
    chain = prompt | llm  # Assuming llm is defined in the main workflow
    response_content = chain.invoke({"input": latest_message}).content.strip()

    ai_message = AIMessage(content=response_content)
    updated_messages = add_messages(state["messages"], ai_message)

    return {"messages": updated_messages, "memory": state["memory"]}

# Create the graph for the generic node
workflow = StateGraph(State)
workflow.add_node("generic", generic_node)

# Add edges
workflow.add_edge(START, "generic")
workflow.add_edge("generic", END)

# Compile the graph
graph = workflow.compile()
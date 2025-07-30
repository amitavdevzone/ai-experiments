from typing import TypedDict, Union
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, Messages
from langchain.tools import Tool
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from tools.car_tools import find_cars, book_car
from memory import Memory

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
llm_car_booking = ChatGroq(api_key=groq_api_key, model="Gemma2-9b-It")

class State(TypedDict):
    messages: list
    intent: Union[str, None]

def car_booking_node(state: State):
    """Handle car booking related queries."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant for car bookings. You can search for cars and book them when needed.",
            ),
            ("human", "{input}"),
        ]
    )

    latest_message = state["messages"][-1].content
    chain = prompt | llm_car_booking
    response_content = chain.invoke({"input": latest_message}).content.strip()

    ai_message = AIMessage(content=response_content)
    updated_messages = add_messages(state["messages"], ai_message)

    return {"messages": updated_messages, "intent": "car_booking"}

# Create tools
search_cars_tool = Tool(
    name="search_cars",
    func=find_cars,
    description="Searches for available cars based on date, car type, and location.",
)

book_car_tool = Tool(
    name="book_car",
    func=book_car,
    description="Books a car using date, location, and type.",
)

# Bind tools to the LLM
llm_car_booking = llm_car_booking.bind_tools(tools=[search_cars_tool, book_car_tool])

# Create the workflow for car booking
workflow = StateGraph(State)
workflow.add_node("car_booking", car_booking_node)

# Add edges
workflow.add_edge(START, "car_booking")
workflow.add_edge("car_booking", END)

# Compile the graph
graph = workflow.compile()
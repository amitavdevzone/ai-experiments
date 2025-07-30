from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages, Messages
from langchain.tools import Tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm_hotel = ChatGroq(api_key=groq_api_key, model="Gemma2-9b-It")

class State(TypedDict):
    messages: List[Messages]
    intent: Union[str, None]

# Tool for finding hotels
def find_hotels(location: str, date: str) -> str:
    # Logic to find hotels based on location and date
    return f"Here are some hotels available in {location} on {date}."

# Tool for booking a hotel
def book_hotel(hotel_id: str, date: str, room_type: str) -> str:
    # Logic to book a hotel
    return f"Hotel with ID {hotel_id} has been booked for {date} as a {room_type}."

# Hotel booking node
def hotel_booking_node(state: State):
    prompt = "You are a helpful assistant for hotel bookings. You can find hotels and book them."
    latest_message = state["messages"][-1].content
    response_content = llm_hotel.invoke({"input": latest_message}).content.strip()

    ai_message = {"role": "assistant", "content": response_content}
    updated_messages = add_messages(state["messages"], ai_message)

    return {"messages": updated_messages, "intent": "hotel_booking"}

# Create tools
find_hotels_tool = Tool(
    name="find_hotels",
    func=find_hotels,
    description="Finds hotels based on location and date."
)

book_hotel_tool = Tool(
    name="book_hotel",
    func=book_hotel,
    description="Books a hotel using hotel ID, date, and room type."
)

# Create tool node
hotel_tools = [find_hotels_tool, book_hotel_tool]

# Build the graph
workflow = StateGraph(State)
workflow.add_node("hotel_booking", hotel_booking_node)

# Add edges
workflow.add_edge(START, "hotel_booking")
workflow.add_edge("hotel_booking", END)

# Compile the graph
graph = workflow.compile()
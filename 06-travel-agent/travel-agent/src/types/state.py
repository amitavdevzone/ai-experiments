from typing import TypedDict, List, Union

class MemoryEntry(TypedDict):
    user_input: str
    assistant_response: str

class State(TypedDict):
    messages: List[str]
    intent: Union[str, None]
    memory: List[MemoryEntry]  # To retain context from previous conversations
    current_location: Union[str, None]  # To store user's current location
    current_date: Union[str, None]  # To store the date for bookings
    hotel_id: Union[str, None]  # To store the selected hotel ID
    car_type: Union[str, None]  # To store the selected car type
    room_type: Union[str, None]  # To store the selected room type
    booking_details: Union[dict, None]  # To store details of the booking made
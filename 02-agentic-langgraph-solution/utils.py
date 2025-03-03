from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os


class Utils:
    @staticmethod
    def get_model():
        load_dotenv()
        groq_api_key = os.getenv("GROQ_API_KEY")
        model = ChatGroq(model="llama3-8b-8192", api_key=groq_api_key)
        return model

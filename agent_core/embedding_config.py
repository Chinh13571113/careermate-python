from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()

google_api_key = os.environ["GOOGLE_API_KEY"]


def load_embedding():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=SecretStr(google_api_key),
    )
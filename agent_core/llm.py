# agent_core/utils/llm.py
import os
from functools import lru_cache
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import logging

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.5-flash"
OPENAI_MODEL_NAME = "gpt-4o"
google_api_key = os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL", "https://aiportalapi.stu-platform.live/jpe")

if not google_api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in environment variables.")


@lru_cache(maxsize=4)
def get_gemini_model(
    temperature: float = 0,
    top_p: float = 1.0,


):
    """
    Create a cached, configured ChatGoogleGenerativeAI model.

    Params:
        temperature: randomness (0 = deterministic, 1 = creative)
        top_p: nucleus sampling (controls diversity)

    Returns:
        Cached LLM instance for better performance
    """
    # Configuration for faster responses
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=google_api_key,
        temperature=temperature,
        top_p=top_p,
        max_tokens=1024,
        timeout=15,

    )

    return llm


@lru_cache(maxsize=4)
def get_openai_model(
    temperature: float = 0,
    top_p: float = 1.0,
):
    """
    Create a cached, configured ChatOpenAI model.

    Params:
        temperature: randomness (0 = deterministic, 1 = creative)
        top_p: nucleus sampling (controls diversity)

    Returns:
        Cached OpenAI LLM instance for better performance
    """
    if not openai_api_key:
        logger.error("❌ OPENAI_API_KEY not found in environment variables")
        raise ValueError("❌ OPENAI_API_KEY not found in environment variables.")

    logger.info(f"🔧 Initializing OpenAI model: {OPENAI_MODEL_NAME}")
    logger.info(f"🌐 Base URL: {openai_base_url}")
    logger.info(f"🔑 API Key present: {bool(openai_api_key)}")

    try:
        llm = ChatOpenAI(
            model=OPENAI_MODEL_NAME,
            api_key=openai_api_key,
            base_url=openai_base_url,
            temperature=temperature,
            top_p=top_p,
            max_tokens=2048,
            timeout=60,  # Increased timeout for Cloud Run
            seed=1234,
            max_retries=3,  # Added retry
            request_timeout=60,  # Added request timeout
        )
        logger.info("✅ OpenAI model initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI model: {str(e)}")
        raise

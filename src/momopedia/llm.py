import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL")



def get_llm(model: str = "xiaomi/mimo-v2-flash:free"):
    return ChatOpenAI(model="xiaomi/mimo-v2-flash:free",temperature=0.0)

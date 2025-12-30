from crewai import LLM
import os
from dotenv import load_dotenv
import sys

load_dotenv()

def get_llm():
    try:
        API_KEY = os.getenv("GEMINI_API_KEY")

        if not API_KEY:
            return None
        
        gemini_llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=API_KEY, 
        temperature=0.7
        )

        return gemini_llm

    except Exception as e:
        print("Exception: ", e)
        return None
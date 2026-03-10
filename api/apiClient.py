from google import genai
import os
from dotenv import load_dotenv
load_dotenv()


def geminiAI (self,prompt:str)->str:
    '''
    Gemini 3 flash preview receives a promt and return the answer in a string
    '''
    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="gemini-3-flash-preview", contents=prompt
    )
    return response.text
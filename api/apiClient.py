from google import genai
import ollama
import os
from dotenv import load_dotenv
load_dotenv()

local_model = 'gemma4:e2b'

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

def geminiEmbed (document):

    client =genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    result = client.models.embed_content(
        model="gemini-embedding-2-preview",
        contents= document
    )
    return result.embeddings[0].values

def ollamaAI (self,prompt:str)->str:
    '''
    Ollama receives a promt and return the answer in a string
    '''
    response = ollama.generate(
        model=local_model,
        prompt=prompt,
    )
    return response['response']

def ollamaEmbed (document):
    response = ollama.embed(
        model=local_model,
        input=document
    )
    return response['embedding']
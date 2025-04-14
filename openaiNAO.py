

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")


client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI()

class MessageRequest(BaseModel):
    message: str

def search_web(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"
    response = requests.get(url)
    data = response.json()
    
    results = []
    for item in data.get("items", [])[:3]:  # On prend les 3 premiers résultats
        results.append(item["snippet"])
    
    return " ".join(results) if results else "Aucune information trouvée."

@app.post("/chat")
async def chat(request: MessageRequest):
    try:
        web_results = search_web(request.message)
        prompt = f"Question: {request.message}\nInformations trouvées sur le web: {web_results}\nRéponse:"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
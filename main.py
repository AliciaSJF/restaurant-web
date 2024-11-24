from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
import json
import os
from fastapi.staticfiles import StaticFiles

# Carga del contexto
with open("restaurant_info.json", "r") as file:
    restaurant_data = json.load(file)

OpenAI.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

app = FastAPI()

# Montar la carpeta estática
app.mount("/static", StaticFiles(directory="static"), name="static")

class UserQuery(BaseModel):
    question: str

@app.post("/chat")
async def chat_with_bot(query: UserQuery):
    prompt = f"""
    Eres un asistente virtual para el restaurante {restaurant_data['name']}.
    Responde solo con la información proporcionada. 
    Si no tienes la respuesta, indica que no sabes la respuesta.

    Información del restaurante:
    - Menú: {restaurant_data['menu']}
    - Horarios: {restaurant_data['horarios']}
    - Ubicación: {restaurant_data['ubicacion']}

    Pregunta: {query.question}
    """
    try:
        # Llamar a la API de OpenAI con el cliente
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente especializado en restaurantes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        # Extraer la respuesta generada por el modelo
        return {"response": completion.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def get_home():
    # Devolver el archivo index.html
    return FileResponse("static/index.html")

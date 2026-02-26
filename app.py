import json
import logging
import re
import httpx
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI-Agent")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# --- КОНФИГУРАЦИЯ ---
# ОБЯЗАТЕЛЬНО: Получи новый ключ в AI Studio!
API_KEY = "ВАШ_НОВЫЙ_КЛЮЧ" 
WORKING_MODEL_URL = None
ALL_RESULTS = []

class TestRequest(BaseModel):
    subject: str
    level: str
    userId: Optional[str] = "default"

class ResultData(BaseModel):
    score: int
    subject: str
    email: Optional[str] = "anonymous"

# ===================== AI CORE =====================

async def get_working_model():
    global WORKING_MODEL_URL
    for version in ["v1", "v1beta"]:
        list_url = f"https://generativelanguage.googleapis.com/{version}/models?key={API_KEY}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(list_url)
                if response.status_code == 200:
                    models_data = response.json()
                    for m in models_data.get("models", []):
                        if "flash" in m["name"] and "generateContent" in m["supportedGenerationMethods"]:
                            logger.info(f"Найдена живая модель: {m['name']} ({version})")
                            return f"https://generativelanguage.googleapis.com/{version}/{m['name']}:generateContent?key={API_KEY}"
        except: continue
    return None

async def call_gemini(prompt: str):
    global WORKING_MODEL_URL
    if not WORKING_MODEL_URL:
        WORKING_MODEL_URL = await get_working_model()
        if not WORKING_MODEL_URL:
            raise HTTPException(status_code=500, detail="API Ключ недействителен или истек.")

    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.8}}
    
    async with httpx.AsyncClient(timeout=40.0) as client:
        try:
            response = await client.post(WORKING_MODEL_URL, json=payload)
            
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="ИИ перегружен (лимит запросов). Подождите 60 сек.")
            
            if response.status_code != 200:
                logger.error(f"Gemini Error: {response.text}")
                raise HTTPException(status_code=500, detail=f"Ошибка API: {response.status_code}")

            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="ИИ думает слишком долго. Попробуйте еще раз.")

# ===================== ROUTES =====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok", "ai_ready": WORKING_MODEL_URL is not None}

@app.post("/register")
async def register(data: dict):
    return {"email": data.get("email"), "name": "Студент", "status": "success"}

@app.post("/generate_test")
async def generate_test(request: TestRequest):
    try:
        prompt = f"Сгенерируй тест: тема {request.subject}, уровень {request.level}. 5 вопросов. СТРОГО JSON: {{\"questions\": [ {{\"question\": \"\", \"options\": [\"\", \"\", \"\", \"\"], \"correctIndex\": 0}} ] }}"
        raw_text = await call_gemini(prompt)
        clean_json = re.sub(r'```json|```', '', raw_text).strip()
        return json.loads(clean_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка формата данных от ИИ.")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_results")
async def analyze_results(data: ResultData):
    ALL_RESULTS.append(data.score)
    feedback = "Хороший результат!"
    try:
        feedback = await call_gemini(f"Дай 1 короткий совет студенту (результат {data.score}% по {data.subject}).")
    except: pass
    return {"scoreMessage": f"Ваш результат: {data.score}%", "feedback": feedback.strip()}

@app.get("/get_teacher_stats")
async def get_teacher_stats():
    if not ALL_RESULTS: return {"studentCount": 0, "avgScore": 0}
    return {"studentCount": len(ALL_RESULTS), "avgScore": round(sum(ALL_RESULTS) / len(ALL_RESULTS))}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
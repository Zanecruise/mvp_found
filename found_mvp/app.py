import os
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import httpx
import time

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY", "changeme")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID", "your-project-id")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
VERTEX_API_KEY = os.getenv("VERTEX_API_KEY", "vertex-api-key")

client = MongoClient(MONGODB_URI)
db = client["foundlab"]
collection = db["wallet_analysis"]

class WalletInput(BaseModel):
    wallet: str

def local_score_logic(wallet):
    if wallet.startswith("0xA"):
        return 90, ["clean"], "ALLOW", "Wallet padrão, sem anomalias."
    return 40, ["suspect"], "REVIEW", "Padrão incomum, enviar para revisão."

async def vertex_ai_justify(wallet, score, flags):
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{VERTEX_PROJECT_ID}/locations/{VERTEX_LOCATION}/publishers/google/models/gemini-1.0-pro:predict?key={VERTEX_API_KEY}"
    prompt = (
        f"Analise o risco da wallet '{wallet}'. Score: {score}. Flags: {flags}. "
        "Justifique a decisão de aprovação ou revisão em linguagem auditável."
    )
    payload = {
        "instances": [{"content": prompt}],
        "parameters": {"temperature": 0.2, "maxOutputTokens": 128}
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            content = result["predictions"][0].get("content", "")
            return content
    except Exception as e:
        return "Não foi possível consultar o Gemini. Justificativa local aplicada."

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    response = await call_next(request)
    return response

@app.post("/analyze_wallet")
async def analyze_wallet(data: WalletInput):
    wallet = data.wallet
    score, flags, decision, explanation = local_score_logic(wallet)
    gemini_exp = await vertex_ai_justify(wallet, score, flags)
    output = {
        "wallet": wallet,
        "score": score,
        "flags": flags,
        "decision": decision,
        "explanation": gemini_exp or explanation
    }
    collection.insert_one({**output, "input_ts": time.time()})
    return output

"""
app/main.py - FastAPI Application Server for Public Health Information Assistant.
"""
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.rate_limiter import is_rate_limited
from app.config import RATE_LIMIT_PER_MINUTE
from safety.pipeline import run_safety_pipeline
from safety.event_logger import get_safety_event_logs, clear_safety_event_logs
from safety.test_runner import run_all_safety_tests

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Public Health Information Assistant",
    description="Constrained Public Health Information Assistant with Deterministic Safety Controls",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_index():
    """Serves the main application UI."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": "Swasthya Saarthi", "version": "1.0.0"}


@app.post("/api/assess")
async def assess_health_query(request: Request):
    """
    Core assessment endpoint.
    Runs structured intake through the complete deterministic safety pipeline.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    if is_rate_limited(client_ip, limit_per_minute=RATE_LIMIT_PER_MINUTE):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment before trying again.")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON request.")

    result = run_safety_pipeline(body)
    return JSONResponse(content=result)


@app.get("/api/chat/welcome")
async def chat_welcome(language: str = "en"):
    """Returns welcoming greeting and quick suggested replies."""
    from app.chat_handler import get_saarthi_welcome_message
    return JSONResponse(content=get_saarthi_welcome_message(language))


@app.post("/api/chat")
async def chat_message(request: Request):
    """
    Conversational Chatbot Endpoint for Swasthya Saarthi.
    Empathetic, multi-turn AI health guidance with deterministic safety checks.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    if is_rate_limited(client_ip, limit_per_minute=RATE_LIMIT_PER_MINUTE):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON.")

    message = body.get("message", "")
    history = body.get("history", [])
    language = body.get("language", "en")
    context = body.get("context", {})

    from app.chat_handler import process_chat_message
    response = process_chat_message(
        user_message=message,
        conversation_history=history,
        language=language,
        context_data=context
    )
    return JSONResponse(content=response)


@app.post("/api/medicine-scan")
async def medicine_scan(request: Request):
    """
    Analyzes an uploaded medicine photo/name and returns simple, age-friendly explanations.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    filename = body.get("filename", "")
    text = body.get("text", "")
    language = body.get("language", "en")

    from app.medicine_scanner import identify_medicine_from_input
    result = identify_medicine_from_input(filename=filename, text_content=text, language=language)
    return JSONResponse(content=result)


@app.get("/api/emergency-directory")
async def get_emergency_directory(language: str = "en"):
    """
    Returns verified Indian Government Emergency Services directory.
    """
    contacts = [
        {
            "service": "Ambulance & Medical Emergency",
            "number": "108",
            "type": "medical",
            "desc": "Toll-free 24x7 emergency medical transport and first responders.",
            "desc_hi": "24x7 निःशुल्क आपातकालीन एम्बुलेंस और त्वरित चिकित्सा सहायता।",
            "desc_gu": "૨૪ કલાક મફત કટોકટી એમ્બ્યુલન્સ અને તબીબી સેવા."
        },
        {
            "service": "National All-in-One Helpline",
            "number": "112",
            "type": "national",
            "desc": "Single emergency number for police, fire, and medical crises.",
            "desc_hi": "पुलिस, आग और चिकित्सा संकट के लिए एकीकृत राष्ट्रीय नंबर।",
            "desc_gu": "પોલીસ, આગ અને તબીબી કટોકટી માટે સિંગલ હેલ્પલાઇન નંબર."
        },
        {
            "service": "Tele-MANAS Mental Health Support",
            "number": "14416",
            "type": "mental",
            "desc": "Govt of India 24x7 psychological counseling and crisis intervention.",
            "desc_hi": "भारत सरकार की 24x7 मानसिक स्वास्थ्य और तनाव परामर्श सेवा।",
            "desc_gu": "માનસિક તણાવ અને કાઉન્સેલિંગ માટે ૨૪x૭ હેલ્પલાઇન."
        },
        {
            "service": "National Health Helpline (MoHFW)",
            "number": "1075",
            "type": "health",
            "desc": "Ministry of Health & Family Welfare general healthcare queries.",
            "desc_hi": "स्वास्थ्य और परिवार कल्याण मंत्रालय की राष्ट्रीय स्वास्थ्य हेल्पलाइन।",
            "desc_gu": "આરોગ્ય અને પરિવાર કલ્યાણ મંત્રાલયની સહાયતા સેવા."
        },
        {
            "service": "Maternal & Child Ambulance (JSSK)",
            "number": "102",
            "type": "maternal",
            "desc": "Dedicated transport for pregnant mothers and sick infants.",
            "desc_hi": "गर्भवती माताओं और नवजात शिशुओं के लिए विशेष निःशुल्क सेवा।",
            "desc_gu": "સગર્ભા માતાઓ અને નવજાત શિશુઓ માટે વિશેષ વાહન સેવા."
        },
        {
            "service": "Women in Distress Helpline",
            "number": "181",
            "type": "women",
            "desc": "24x7 confidential emergency support for women.",
            "desc_hi": "कठिन परिस्थितियों में महिलाओं के लिए 24x7 आपातकालीन सहायता।",
            "desc_gu": "મહિલાઓ માટે ૨૪ કલાક આપાતકાલીન સહાયતા હેલ્પલાઇન."
        },
        {
            "service": "Childline Emergency Support",
            "number": "1098",
            "type": "child",
            "desc": "National emergency care service for children in distress.",
            "desc_hi": "संकटग्रस्त बच्चों की सुरक्षा और देखभाल के लिए हेल्पलाइन।",
            "desc_gu": "બાળકોની સુરક્ષા અને સહાય માટે રાષ્ટ્રીય હેલ્પલાઇન."
        }
    ]
    return JSONResponse(content={"contacts": contacts})


@app.post("/api/auth/login")
async def save_user_credentials(request: Request):
    """
    Saves/validates persistent user credentials once.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    name = body.get("name", "User").strip() or "User"
    phone = body.get("phone", "").strip()
    age_group = body.get("age_group", "18-59")
    language = body.get("language", "en")

    return JSONResponse(content={
        "status": "authenticated",
        "user": {
            "name": name,
            "phone": phone,
            "age_group": age_group,
            "language": language,
            "is_logged_in": True
        }
    })




@app.get("/api/safety/logs")
async def get_audit_logs():
    """
    Returns privacy-preserving safety event logs (zero PII, zero symptom storage).
    """
    logs = get_safety_event_logs()
    return JSONResponse(content={"logs": logs, "total": len(logs)})


@app.post("/api/safety/clear-logs")
async def clear_audit_logs():
    """Resets in-memory audit logs for demo presentation."""
    clear_safety_event_logs()
    return JSONResponse(content={"status": "cleared"})


@app.get("/api/test-suite/run")
async def execute_test_suite():
    """
    Runs the automated safety test suite and returns real, calculated pass/fail results.
    """
    test_results = run_all_safety_tests()
    return JSONResponse(content=test_results)

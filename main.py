from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# All model imports
from app.modules.users.models import User
from app.modules.assistive.models import SpeechLog
from app.modules.routines import models as routine_models
from app.modules.schemes.models import GovernmentScheme
from app.modules.chatbot.models import ChatSession, ChatMessage


# All router imports
from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.assistive.routes import router as assistive_router
from app.modules.routines.routes import router as routine_router
from app.modules.schemes.routes import router as schemes_router
from app.modules.chatbot.routes import router as chatbot_router


app = FastAPI(title="Assistive Platform API")
BASE_DIR = os.path.dirname(__file__)
WEB_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
PAGES_ROOT = os.path.join(WEB_ROOT, "pages")

# ✅ Middleware FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routers AFTER middleware
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(assistive_router, prefix="/assistive", tags=["Assistive"])
app.include_router(routine_router, prefix="/routines", tags=["Routines"])
app.include_router(schemes_router, prefix="/schemes", tags=["Government Schemes"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])

# Serve split frontend assets (css/js/images)
app.mount("/static", StaticFiles(directory=os.path.join(WEB_ROOT, "static")), name="static")

@app.get("/app")
def serve_frontend():
    file_path = os.path.join(PAGES_ROOT, "login.html")
    if not os.path.exists(file_path):
        file_path = "index.html"
    return FileResponse(file_path)


@app.get("/app/{page_name}")
def serve_frontend_page(page_name: str):
    file_path = os.path.join(PAGES_ROOT, page_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(file_path)

@app.get("/doctor")
def serve_doctor():
    file_path = os.path.join(PAGES_ROOT, "virtualdoctor.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Virtual doctor page not found")
    return FileResponse(file_path)
@app.get("/")
def health_check():
    return {"status": "API running successfully"}

# ✅ Tables created ONCE here
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
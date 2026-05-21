from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middlewares.exception_handlers import catch_exception_middleware
from routes.upload_pdfs import router as upload_router
from routes.ask_question import router as ask_router

app = FastAPI(
    title="Medical Assistant API",
    description="API for AI Medical Assistant Chatbot"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://medical-assistant-ai-eight.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# middleware exception handlers
app.middleware("http")(catch_exception_middleware)

# routers
app.include_router(upload_router)
app.include_router(ask_router)


@app.get("/")
def home():
    return {"message": "Medical Assistant API Running"}
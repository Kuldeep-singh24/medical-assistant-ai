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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware exception handlers
app.middleware("http")(catch_exception_middleware)

# Routers

# 1. Upload PDF documents
app.include_router(upload_router)

# 2. Asking query
app.include_router(ask_router)
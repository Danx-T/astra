"""
Astra — Ana Uygulama (FastAPI).
API endpoint'lerini tanımlar, modülleri başlatır ve frontend'i serve eder.

Çalıştırma:
    uvicorn main:app --reload
"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Logging ayarları ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# --- Uygulama başlatma/kapatma lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıcında DB ve skill'leri yükle."""
    # DB tablolarını oluştur
    from memory.models import init_db
    init_db()
    logger.info("Veritabanı hazır (SQLite)")

    # Tool'ları import et (registry'ye kaydolmaları için)
    import tools.calculator  # noqa: F401
    import tools.file_ops    # noqa: F401
    import tools.web_search  # noqa: F401
    logger.info("Tool'lar yüklendi")

    # Skill'leri yükle
    from skills.loader import load_all_skills
    load_all_skills()
    logger.info("Skill'ler yüklendi")

    from tools.registry import get_tool_names
    logger.info(f"Kayıtlı tool'lar: {get_tool_names()}")

    logger.info("🚀 Astra hazır!")
    yield
    logger.info("Astra kapatılıyor...")


# --- FastAPI uygulaması ---
app = FastAPI(
    title="Astra — Mini AI Agent Platform",
    description="LLM + Tools + Skills + Memory + Agent Loop",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — local development için tüm origin'lere açık
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static dosyaları serve et (CSS, JS, vb.)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# --- Pydantic Modelleri ---
class MessageRequest(BaseModel):
    """Kullanıcı mesajı isteği."""
    message: str


class MessageResponse(BaseModel):
    """Agent yanıtı."""
    response: str
    tool_calls_made: list = []


class ConversationResponse(BaseModel):
    """Conversation bilgisi."""
    id: str
    title: str
    created_at: str | None = None


# --- API Endpoint'leri ---

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Frontend chat arayüzünü serve eder."""
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend dosyası bulunamadı")
    return FileResponse(str(index_path))


@app.post("/conversations", response_model=ConversationResponse)
async def create_conversation():
    """Yeni bir conversation oluşturur ve ID'sini döner."""
    from memory.store import create_conversation, get_conversation
    conv_id = create_conversation()
    conv = get_conversation(conv_id)
    return conv


@app.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations():
    """Tüm conversation'ları listeler."""
    from memory.store import get_all_conversations
    return get_all_conversations()


@app.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    """Bir conversation'ın mesaj geçmişini döner."""
    from memory.store import get_conversation, get_conversation_history
    conv = get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation bulunamadı")

    messages = get_conversation_history(conversation_id)
    # System mesajlarını filtrele (frontend'e göstermeye gerek yok)
    filtered = [m for m in messages if m["role"] != "system"]
    return {"conversation_id": conversation_id, "messages": filtered}


@app.post("/conversations/{conversation_id}/message", response_model=MessageResponse)
async def send_message(conversation_id: str, request: MessageRequest):
    """
    Kullanıcı mesajını alır, agent loop'u çalıştırır ve yanıtı döner.
    Bu endpoint tüm tool calling sürecini yönetir.
    """
    from memory.store import get_conversation, update_conversation_title
    from agent.loop import run_agent

    conv = get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation bulunamadı")

    # Agent loop'u çalıştır
    result = run_agent(conversation_id, request.message)

    # İlk mesajda conversation başlığını güncelle
    if conv.get("title") == "Yeni Konuşma":
        # İlk kullanıcı mesajının ilk 50 karakterini başlık yap
        title = request.message[:50] + ("..." if len(request.message) > 50 else "")
        update_conversation_title(conversation_id, title)

    return MessageResponse(
        response=result["response"],
        tool_calls_made=result["tool_calls_made"],
    )

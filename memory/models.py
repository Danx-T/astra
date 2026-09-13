"""
Astra — Veritabanı Modelleri (SQLAlchemy).
SQLite dosya tabanlı veritabanı ile conversation ve message tablolarını tanımlar.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DATABASE_URL

# SQLAlchemy engine ve session
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Conversation(Base):
    """Konuşma tablosu — her chat oturumu bir conversation."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    title = Column(String, default="Yeni Konuşma")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # İlişki: bir conversation'ın birçok mesajı olabilir
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """Mesaj tablosu — her mesaj bir conversation'a bağlı."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "system", "user", "assistant", "tool"
    content = Column(Text, nullable=True)  # Mesaj içeriği (tool_call mesajlarında None olabilir)
    tool_calls = Column(Text, nullable=True)  # JSON string — LLM'in tool çağrıları
    tool_call_id = Column(String, nullable=True)  # Tool yanıtlarında tool_call referans ID'si
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # İlişki
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conv={self.conversation_id})>"


def init_db():
    """Veritabanı tablolarını oluşturur (yoksa). Uygulama başlangıcında çağrılır."""
    Base.metadata.create_all(bind=engine)

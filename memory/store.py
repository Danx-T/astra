"""
Astra — Memory Store (Bellek Deposu).
Conversation ve message CRUD işlemleri.
Agent loop bu fonksiyonlar üzerinden mesaj geçmişini kaydet/oku yapar.
"""

import json
import logging
import uuid
from memory.models import SessionLocal, Conversation, Message

logger = logging.getLogger(__name__)


def create_conversation(title: str = "Yeni Konuşma") -> str:
    """
    Yeni bir conversation oluşturur.

    Returns:
        str: Oluşturulan conversation'ın ID'si (UUID)
    """
    conversation_id = str(uuid.uuid4())

    with SessionLocal() as session:
        conv = Conversation(id=conversation_id, title=title)
        session.add(conv)
        session.commit()
        logger.info(f"Yeni conversation oluşturuldu: {conversation_id}")

    return conversation_id


def get_conversation(conversation_id: str) -> dict | None:
    """
    Tek bir conversation'ın bilgilerini döner.

    Returns:
        dict veya None
    """
    with SessionLocal() as session:
        conv = session.query(Conversation).filter_by(id=conversation_id).first()
        if not conv:
            return None
        return {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
        }


def save_message(
    conversation_id: str,
    role: str,
    content: str | None = None,
    tool_calls: list | None = None,
    tool_call_id: str | None = None,
) -> int:
    """
    Mesajı veritabanına kaydeder.

    Args:
        conversation_id: Mesajın ait olduğu conversation
        role:            "user", "assistant", "tool", "system"
        content:         Mesaj içeriği
        tool_calls:      LLM'in tool çağrıları (list of dict, JSON olarak saklanır)
        tool_call_id:    Tool yanıtlarında referans ID

    Returns:
        int: Kaydedilen mesajın ID'si
    """
    with SessionLocal() as session:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=json.dumps(tool_calls) if tool_calls else None,
            tool_call_id=tool_call_id,
            # created_at SQLAlchemy model default ile otomatik atanır
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)
        msg_id = msg.id
        logger.debug(f"Mesaj kaydedildi: role={role}, conv={conversation_id}, id={msg_id}")
        return msg_id


def get_conversation_history(conversation_id: str) -> list[dict]:
    """
    Bir conversation'ın tüm mesaj geçmişini LLM'e uygun formatta döner.

    Returns:
        list[dict]: OpenAI messages formatında mesaj listesi
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "...", "tool_calls": [...]}, ...]
    """
    with SessionLocal() as session:
        messages = (
            session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at)
            .all()
        )

        result = []
        for msg in messages:
            entry = {"role": msg.role}

            # Content ekle (None olabilir — tool_call mesajlarında)
            if msg.content is not None:
                entry["content"] = msg.content
            else:
                # OpenAI API bazı durumlarda content'in None yerine boş string olmasını ister
                entry["content"] = ""

            # Tool çağrıları varsa ekle (assistant mesajlarında)
            if msg.tool_calls:
                try:
                    entry["tool_calls"] = json.loads(msg.tool_calls)
                except json.JSONDecodeError:
                    pass

            # Tool yanıtı ise tool_call_id ekle
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id

            result.append(entry)

        return result


def get_all_conversations() -> list[dict]:
    """Tüm conversation'ların listesini döner (son oluşturulan önce)."""
    with SessionLocal() as session:
        convs = (
            session.query(Conversation)
            .order_by(Conversation.created_at.desc())
            .all()
        )
        return [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in convs
        ]


def update_conversation_title(conversation_id: str, title: str) -> None:
    """Conversation başlığını günceller."""
    with SessionLocal() as session:
        conv = session.query(Conversation).filter_by(id=conversation_id).first()
        if conv:
            conv.title = title
            session.commit()

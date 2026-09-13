"""
Astra — Agent Loop (Ana Döngü).
LLM + Tool Calling döngüsünü yönetir. Bu modül tüm sistemin kalbidir:
1. Kullanıcı mesajını alır
2. Conversation history'yi DB'den çeker
3. System prompt oluşturur (tool'lar + skill'ler dahil)
4. LLM'i iteratif olarak çağırır (tool call → execute → tekrar sor)
5. Final cevabı döner

Yeni tool eklemek için bu dosyaya dokunmanıza GEREK YOK —
tool registry otomatik olarak yeni tool'ları agent loop'a dahil eder.
"""

import json
import logging
from config import MAX_AGENT_ITERATIONS
from llm.client import call_llm
from tools.registry import get_all_tool_schemas, execute_tool
from skills.loader import get_skill_summaries
from memory.store import save_message, get_conversation_history

logger = logging.getLogger(__name__)


def _build_system_prompt() -> str:
    """
    Agent'ın system prompt'unu oluşturur.
    Tool listesi ve skill özetlerini içerir.
    """
    skill_summaries = get_skill_summaries()

    return f"""Sen Astra, güçlü ve yardımsever bir AI asistansın.

## Yeteneklerin
- Kullanıcının sorularını yanıtlayabilirsin.
- Çeşitli tool'ları kullanarak hesaplama yapabilir, dosya okuyup yazabilir, web araması yapabilirsin.
- Skill'leri yükleyerek belirli alanlarda uzmanlaşmış talimatları takip edebilirsin.

## Tool Kullanım Kuralları
- Bir hesaplama gerektiğinde `calculator` tool'unu kullan, kafadan hesaplama yapma.
- Dosya okuma/yazma için `read_file` ve `write_file` tool'larını kullan.
- İnternet araştırması gerektiğinde `web_search` tool'unu kullan.
- Belirli bir alanda derinlemesine yardım gerektiğinde önce ilgili skill'i `load_skill` ile yükle.

## Yanıt Kuralları
- Her zaman Türkçe yanıt ver (kullanıcı başka dilde sormadıkça).
- Net, yapılandırılmış ve yardımsever ol.
- Tool sonuçlarını kullanıcıya anlamlı bir şekilde sun, ham veriyi olduğu gibi yapıştırma.

{skill_summaries}
"""


def run_agent(conversation_id: str, user_message: str) -> dict:
    """
    Agent loop'unu çalıştırır.

    Args:
        conversation_id: Mevcut konuşmanın ID'si
        user_message:    Kullanıcının gönderdiği mesaj

    Returns:
        dict: {
            "response": str,           # Agent'ın final yanıtı
            "tool_calls_made": list,    # Yapılan tool çağrılarının özeti
        }
    """
    logger.info(f"=== Agent Loop Başladı === conv={conversation_id}")
    logger.info(f"Kullanıcı mesajı: {user_message[:100]}...")

    # 1. Kullanıcı mesajını DB'ye kaydet
    save_message(conversation_id, role="user", content=user_message)

    # 2. Conversation history'yi DB'den çek
    history = get_conversation_history(conversation_id)

    # 3. System prompt oluştur
    system_prompt = _build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}] + history

    # 4. Tool tanımlarını al
    tools = get_all_tool_schemas()
    tool_calls_log = []  # Yapılan tool çağrılarının kaydı

    # 5. Agent Loop (iteratif tool calling)
    for iteration in range(1, MAX_AGENT_ITERATIONS + 1):
        logger.info(f"--- İterasyon {iteration}/{MAX_AGENT_ITERATIONS} ---")

        # LLM'i çağır
        llm_response = call_llm(messages, tools=tools if tools else None)

        # Tool call var mı kontrol et
        if llm_response.get("tool_calls"):
            # Asistanın tool_call mesajını history'ye ve DB'ye ekle
            assistant_msg = {
                "role": "assistant",
                "content": llm_response.get("content") or "",
                "tool_calls": llm_response["tool_calls"],
            }
            messages.append(assistant_msg)
            save_message(
                conversation_id,
                role="assistant",
                content=llm_response.get("content"),
                tool_calls=llm_response["tool_calls"],
            )

            # Her tool call'ı çalıştır
            for tool_call in llm_response["tool_calls"]:
                tc_id = tool_call["id"]
                func_name = tool_call["function"]["name"]
                func_args = tool_call["function"]["arguments"]

                logger.info(f"🔧 Tool çağrılıyor: {func_name}({func_args})")

                # Tool'u çalıştır
                result = execute_tool(func_name, func_args)

                logger.info(f"✅ Tool sonucu ({func_name}): {str(result)[:200]}")

                # Tool sonucunu history'ye ve DB'ye ekle
                tool_msg = {
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tc_id,
                }
                messages.append(tool_msg)
                save_message(
                    conversation_id,
                    role="tool",
                    content=result,
                    tool_call_id=tc_id,
                )

                # Log kaydı
                tool_calls_log.append({
                    "iteration": iteration,
                    "tool": func_name,
                    "args": func_args,
                    "result": str(result)[:500],
                })

            # Loop devam — LLM'e tekrar sor
            continue

        else:
            # Final cevap geldi — tool call yok
            final_content = llm_response.get("content") or "Yanıt üretilemedi."

            logger.info(f"💬 Final cevap alındı (iterasyon {iteration})")

            # Final cevabı DB'ye kaydet
            save_message(conversation_id, role="assistant", content=final_content)

            logger.info(f"=== Agent Loop Tamamlandı === (toplam {iteration} iterasyon)")

            return {
                "response": final_content,
                "tool_calls_made": tool_calls_log,
            }

    # Max iterasyona ulaşıldı — sonsuz döngü koruması
    timeout_msg = (
        "⚠️ İşlem çok uzun sürdü ve maksimum adım sayısına ulaşıldı. "
        "Lütfen sorunuzu daha basit bir şekilde ifade edip tekrar deneyin."
    )
    logger.warning(f"Agent loop max iterasyona ulaştı ({MAX_AGENT_ITERATIONS})")
    save_message(conversation_id, role="assistant", content=timeout_msg)

    return {
        "response": timeout_msg,
        "tool_calls_made": tool_calls_log,
    }

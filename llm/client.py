"""
Astra — LLM İstemci Katmanı.
GroqCloud API'sine OpenAI-uyumlu SDK ile bağlanır.
Tool calling (function calling) formatını destekler.
Hata yönetimi: API hatası, rate limit, timeout yakalanır.
"""

import logging
from openai import OpenAI, APIError, RateLimitError, APITimeoutError, APIConnectionError
from config import GROQ_API_KEY, GROQ_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

# Groq'a yönlendirilmiş OpenAI istemcisi (singleton)
_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)


def call_llm(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """
    LLM'e istek gönderir ve yanıtı döndürür.

    Args:
        messages: OpenAI formatında mesaj listesi
                  [{"role": "system"|"user"|"assistant"|"tool", "content": "..."}]
        tools:    Opsiyonel — OpenAI tool tanım listesi (function calling için)

    Returns:
        dict: {
            "role": "assistant",
            "content": str | None,
            "tool_calls": list | None  # tool çağrıları varsa
        }

    Raises:
        Hata durumlarında anlamlı mesaj içeren dict döner, exception fırlatmaz.
    """
    try:
        # API çağrısı parametreleri
        kwargs = {
            "model": LLM_MODEL,
            "messages": messages,
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_TOKENS,
        }

        # Tool tanımları varsa ekle
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        logger.info(f"LLM çağrısı yapılıyor — model: {LLM_MODEL}, mesaj sayısı: {len(messages)}")

        response = _client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        # Yanıtı standart dict formatına dönüştür
        result = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": None,
        }

        # Tool call'lar varsa ekle
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,  # JSON string
                    },
                }
                for tc in message.tool_calls
            ]
            logger.info(
                f"LLM tool çağrısı döndü: "
                f"{[tc['function']['name'] for tc in result['tool_calls']]}"
            )
        else:
            logger.info(f"LLM final cevap döndü (uzunluk: {len(message.content or '')} karakter)")

        return result

    except RateLimitError as e:
        logger.error(f"Rate limit aşıldı: {e}")
        return {
            "role": "assistant",
            "content": "⚠️ API rate limit aşıldı. Lütfen biraz bekleyip tekrar deneyin.",
            "tool_calls": None,
        }

    except APITimeoutError as e:
        logger.error(f"API zaman aşımı: {e}")
        return {
            "role": "assistant",
            "content": "⚠️ API isteği zaman aşımına uğradı. Lütfen tekrar deneyin.",
            "tool_calls": None,
        }

    except APIConnectionError as e:
        logger.error(f"API bağlantı hatası: {e}")
        return {
            "role": "assistant",
            "content": "⚠️ API'ye bağlanılamadı. İnternet bağlantınızı kontrol edin.",
            "tool_calls": None,
        }

    except APIError as e:
        logger.error(f"API hatası: {e}")
        return {
            "role": "assistant",
            "content": f"⚠️ API hatası oluştu: {e.message}",
            "tool_calls": None,
        }

    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}", exc_info=True)
        return {
            "role": "assistant",
            "content": f"⚠️ Beklenmeyen bir hata oluştu: {str(e)}",
            "tool_calls": None,
        }

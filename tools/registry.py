"""
Astra — Tool Registry (Kayıt Sistemi).
Tool'ları decorator ile kaydeder, LLM'e gönderilecek tool tanımlarını
ve çalıştırma fonksiyonlarını yönetir.

Yeni tool eklemek için:
1. tools/ altında yeni bir .py dosyası oluştur
2. Fonksiyonunu @register_tool ile dekore et
3. İlgili dosyayı tools/__init__.py'de import et (veya main.py'de)
   — agent/loop.py'ye dokunmana gerek yok.
"""

import json
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

# Tool kayıt deposu: { "tool_name": { "function": callable, "schema": dict } }
_registry: dict[str, dict[str, Any]] = {}


def register_tool(
    name: str,
    description: str,
    parameters: dict,
) -> Callable:
    """
    Tool kaydeden decorator.

    Args:
        name:        Tool'un benzersiz adı (LLM bunu görür)
        description: Tool'un ne yaptığını açıklayan metin (LLM bunu okur)
        parameters:  JSON Schema formatında parametre tanımı

    Kullanım:
        @register_tool(
            name="calculator",
            description="Matematiksel ifadeleri hesaplar",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Hesaplanacak ifade"}
                },
                "required": ["expression"]
            }
        )
        def calculator(expression: str) -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        _registry[name] = {
            "function": func,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            },
        }
        logger.info(f"Tool kaydedildi: {name}")
        return func
    return decorator


def get_all_tool_schemas() -> list[dict]:
    """LLM'e gönderilecek OpenAI-uyumlu tool tanım listesini döner."""
    return [entry["schema"] for entry in _registry.values()]


def get_tool_names() -> list[str]:
    """Kayıtlı tüm tool isimlerini döner."""
    return list(_registry.keys())


def execute_tool(name: str, arguments: str) -> str:
    """
    Belirtilen tool'u çalıştırır ve sonucunu string olarak döner.

    Args:
        name:      Çalıştırılacak tool'un adı
        arguments: JSON string formatında argümanlar

    Returns:
        Tool'un sonucu (string). Hata durumunda "Tool failed: <sebep>" döner.
    """
    if name not in _registry:
        error_msg = f"Tool bulunamadı: {name}"
        logger.error(error_msg)
        return f"Tool failed: {error_msg}"

    try:
        # JSON argümanları parse et
        args = json.loads(arguments) if arguments else {}
        logger.info(f"Tool çalıştırılıyor: {name}({args})")

        # Tool fonksiyonunu çağır
        result = _registry[name]["function"](**args)

        logger.info(f"Tool sonucu ({name}): {str(result)[:200]}")
        return str(result)

    except json.JSONDecodeError as e:
        error_msg = f"Geçersiz JSON argüman: {e}"
        logger.error(f"Tool hatası ({name}): {error_msg}")
        return f"Tool failed: {error_msg}"

    except TypeError as e:
        error_msg = f"Yanlış argümanlar: {e}"
        logger.error(f"Tool hatası ({name}): {error_msg}")
        return f"Tool failed: {error_msg}"

    except Exception as e:
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.error(f"Tool hatası ({name}): {error_msg}", exc_info=True)
        return f"Tool failed: {error_msg}"

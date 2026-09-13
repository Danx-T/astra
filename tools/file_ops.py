"""
Astra — Dosya İşlemleri Tool'ları.
workspace/ dizini altında güvenli dosya okuma ve yazma.
Path traversal saldırılarına karşı korumalı — workspace dışına erişim engellenir.
"""

import os
from pathlib import Path
from tools.registry import register_tool
from config import WORKSPACE_DIR


def _safe_resolve(path: str) -> Path:
    """
    Verilen yolu workspace içinde güvenli şekilde çözümler.
    Path traversal (../../etc/passwd gibi) saldırılarını engeller.

    Raises:
        ValueError: Yol workspace dışına çıkıyorsa
    """
    # Yolu workspace altında birleştir ve mutlak yola çevir
    resolved = (WORKSPACE_DIR / path).resolve()

    # Workspace dışına çıkıp çıkmadığını kontrol et
    workspace_resolved = WORKSPACE_DIR.resolve()
    if not str(resolved).startswith(str(workspace_resolved)):
        raise ValueError(
            f"Güvenlik hatası: '{path}' yolu workspace dışına çıkıyor. "
            f"Yalnızca workspace/ dizini altındaki dosyalara erişebilirsiniz."
        )

    return resolved


@register_tool(
    name="read_file",
    description=(
        "Workspace dizini altındaki bir dosyayı okur ve içeriğini döndürür. "
        "Yalnızca workspace/ klasörü altındaki dosyalara erişim izni vardır. "
        "Örnek: read_file(path='test.txt') veya read_file(path='alt_klasor/dosya.md')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Okunacak dosyanın workspace/ dizinine göre bağıl yolu",
            }
        },
        "required": ["path"],
    },
)
def read_file(path: str) -> str:
    """Workspace altındaki bir dosyayı okur."""
    try:
        resolved = _safe_resolve(path)

        if not resolved.exists():
            return f"Dosya bulunamadı: {path}"

        if not resolved.is_file():
            return f"Bu bir dosya değil: {path}"

        content = resolved.read_text(encoding="utf-8")
        return f"--- {path} içeriği ---\n{content}"

    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Dosya okuma hatası: {str(e)}"


@register_tool(
    name="write_file",
    description=(
        "Workspace dizini altına dosya yazar veya üzerine yazar. "
        "Gerekirse ara dizinleri otomatik oluşturur. "
        "Yalnızca workspace/ klasörü altına yazma izni vardır. "
        "Örnek: write_file(path='test.txt', content='Merhaba dünya!')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Yazılacak dosyanın workspace/ dizinine göre bağıl yolu",
            },
            "content": {
                "type": "string",
                "description": "Dosyaya yazılacak içerik",
            },
        },
        "required": ["path", "content"],
    },
)
def write_file(path: str, content: str) -> str:
    """Workspace altına dosya yazar."""
    try:
        resolved = _safe_resolve(path)

        # Gerekirse üst dizinleri oluştur
        resolved.parent.mkdir(parents=True, exist_ok=True)

        resolved.write_text(content, encoding="utf-8")
        return f"Dosya başarıyla yazıldı: {path} ({len(content)} karakter)"

    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Dosya yazma hatası: {str(e)}"

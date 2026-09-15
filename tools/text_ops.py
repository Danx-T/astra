"""
Astra — Metin İşleme Tool'ları.
Metin özetleme, sayma, dönüştürme ve arama işlemleri.
LLM'e gitmeden yapılabilecek basit metin manipülasyonları.
"""

import re
import hashlib
import json
from tools.registry import register_tool


@register_tool(
    name="text_stats",
    description=(
        "Bir metnin istatistiklerini çıkarır: karakter sayısı, kelime sayısı, "
        "satır sayısı, cümle sayısı ve benzersiz kelime sayısı. "
        "Örnek: text_stats(text='Merhaba dünya! Bu bir test.')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Analiz edilecek metin",
            }
        },
        "required": ["text"],
    },
)
def text_stats(text: str) -> str:
    """Metin istatistikleri çıkarır."""
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    words = text.split()
    word_count = len(words)
    lines = text.splitlines()
    line_count = len(lines) if text else 0
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    unique_words = len(set(w.lower().strip(".,!?;:\"'()") for w in words))

    return (
        f"📊 **Metin İstatistikleri**\n"
        f"- Karakter: {chars:,} (boşluksuz: {chars_no_space:,})\n"
        f"- Kelime: {word_count:,}\n"
        f"- Benzersiz kelime: {unique_words:,}\n"
        f"- Satır: {line_count:,}\n"
        f"- Cümle: {sentence_count:,}"
    )


@register_tool(
    name="text_transform",
    description=(
        "Metin dönüşüm işlemleri yapar. "
        "Desteklenen işlemler: uppercase, lowercase, title, reverse, "
        "sort_lines, unique_lines, remove_blank_lines, trim. "
        "Örnek: text_transform(text='merhaba dünya', operation='uppercase')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Dönüştürülecek metin",
            },
            "operation": {
                "type": "string",
                "description": "Dönüşüm işlemi",
                "enum": [
                    "uppercase", "lowercase", "title", "reverse",
                    "sort_lines", "unique_lines", "remove_blank_lines", "trim",
                ],
            },
        },
        "required": ["text", "operation"],
    },
)
def text_transform(text: str, operation: str) -> str:
    """Metin dönüşüm işlemi uygular."""
    ops = {
        "uppercase": lambda t: t.upper(),
        "lowercase": lambda t: t.lower(),
        "title": lambda t: t.title(),
        "reverse": lambda t: t[::-1],
        "sort_lines": lambda t: "\n".join(sorted(t.splitlines())),
        "unique_lines": lambda t: "\n".join(dict.fromkeys(t.splitlines())),
        "remove_blank_lines": lambda t: "\n".join(
            line for line in t.splitlines() if line.strip()
        ),
        "trim": lambda t: "\n".join(line.strip() for line in t.splitlines()),
    }

    if operation not in ops:
        return f"Geçersiz işlem: {operation}. Desteklenenler: {list(ops.keys())}"

    return ops[operation](text)


@register_tool(
    name="regex_search",
    description=(
        "Metin içinde regex (düzenli ifade) araması yapar. "
        "Eşleşen tüm sonuçları döndürür. "
        "Örnek: regex_search(text='Tel: 555-1234, Fax: 555-5678', pattern=r'\\d{3}-\\d{4}')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Aranacak metin",
            },
            "pattern": {
                "type": "string",
                "description": "Regex pattern'i",
            },
        },
        "required": ["text", "pattern"],
    },
)
def regex_search(text: str, pattern: str) -> str:
    """Metin içinde regex araması yapar."""
    try:
        matches = re.findall(pattern, text)
        if not matches:
            return f"'{pattern}' pattern'i için eşleşme bulunamadı."

        return (
            f"🔍 {len(matches)} eşleşme bulundu:\n"
            + "\n".join(f"  {i+1}. {m}" for i, m in enumerate(matches[:50]))
        )
    except re.error as e:
        return f"Geçersiz regex: {e}"


@register_tool(
    name="hash_text",
    description=(
        "Metin veya dosya için hash değeri hesaplar (MD5, SHA256). "
        "Dosya bütünlüğü kontrolü veya karşılaştırma için kullanılır. "
        "Örnek: hash_text(text='merhaba', algorithm='sha256')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Hash'lenecek metin",
            },
            "algorithm": {
                "type": "string",
                "description": "Hash algoritması (md5, sha256)",
                "enum": ["md5", "sha256"],
                "default": "sha256",
            },
        },
        "required": ["text"],
    },
)
def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Hash değeri hesaplar."""
    algos = {
        "md5": hashlib.md5,
        "sha256": hashlib.sha256,
    }
    if algorithm not in algos:
        return f"Geçersiz algoritma: {algorithm}. Desteklenenler: {list(algos.keys())}"

    h = algos[algorithm](text.encode("utf-8")).hexdigest()
    return f"🔐 {algorithm.upper()}: {h}"


@register_tool(
    name="json_format",
    description=(
        "JSON metnini güzel formata (pretty print) dönüştürür veya "
        "JSON doğrulaması yapar. Geçersiz JSON hatalarını raporlar. "
        "Örnek: json_format(text='{\"a\":1,\"b\":2}')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Formatlanacak JSON metni",
            }
        },
        "required": ["text"],
    },
)
def json_format(text: str) -> str:
    """JSON'u formatlar ve doğrular."""
    try:
        parsed = json.loads(text)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        return f"✅ Geçerli JSON ({type(parsed).__name__}):\n\n{formatted}"
    except json.JSONDecodeError as e:
        return f"❌ Geçersiz JSON: {e}"

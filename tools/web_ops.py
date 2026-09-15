"""
Astra — Web İçerik Çekme Tool'u.
Bir URL'in tam içeriğini HTTP GET ile çeker, HTML'i temiz metne dönüştürür.
httpx kütüphanesi kullanılır (openai bağımlılığı olarak zaten kurulu).
"""

import re
import logging
from tools.registry import register_tool

logger = logging.getLogger(__name__)


def _html_to_text(html: str) -> str:
    """Basit HTML → düz metin dönüşümü (gereksiz tag ve script'leri temizler)."""
    # Script ve style bloklarını kaldır
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # HTML yorumlarını kaldır
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    # Blok elementleri newline'a çevir
    html = re.sub(r"<(br|p|div|h[1-6]|li|tr)[^>]*>", "\n", html, flags=re.IGNORECASE)
    # Kalan tag'leri kaldır
    html = re.sub(r"<[^>]+>", "", html)
    # HTML entity'leri dönüştür
    html = html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    html = html.replace("&nbsp;", " ").replace("&quot;", '"').replace("&#39;", "'")
    # Fazla boşlukları temizle
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = re.sub(r"[ \t]+", " ", html)
    return html.strip()


@register_tool(
    name="web_fetch",
    description=(
        "Belirtilen URL'in tam içeriğini çeker ve okunabilir düz metin olarak döndürür. "
        "web_search yalnızca snippet döndürürken bu tool sayfanın tüm içeriğine erişir. "
        "Dokümantasyon, makale veya API yanıtı okumak için kullanılır. "
        "Örnek: web_fetch(url='https://docs.python.org/3/library/json.html')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "İçeriği çekilecek URL",
            },
            "max_chars": {
                "type": "integer",
                "description": "Döndürülecek maksimum karakter sayısı (varsayılan 5000)",
                "default": 5000,
            },
        },
        "required": ["url"],
    },
)
def web_fetch(url: str, max_chars: int = 5000) -> str:
    """URL içeriğini çeker ve temiz metin olarak döndürür."""
    try:
        import httpx

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        logger.info(f"web_fetch: {url}")
        response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")

        # JSON yanıtı
        if "application/json" in content_type:
            text = response.text[:max_chars]
            return f"🌐 {url}\n[JSON yanıtı]\n\n{text}"

        # HTML yanıtı → temiz metin
        if "html" in content_type or content_type == "":
            text = _html_to_text(response.text)
        else:
            text = response.text

        # Karakter limiti uygula
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n[... içerik {len(text)} karakterden kısaltıldı]"

        return f"🌐 {url}\n[HTTP {response.status_code}]\n\n{text}"

    except Exception as e:
        return f"web_fetch hatası: {str(e)}"

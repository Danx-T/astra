"""
Astra — Genel HTTP İstek Tool'u.
REST API çağrıları, webhook tetikleme ve 3. taraf servis entegrasyonu için.
httpx kütüphanesi kullanılır.
"""

import json
import logging
from tools.registry import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="http_request",
    description=(
        "Genel amaçlı HTTP isteği gönderir (GET, POST, PUT, DELETE, PATCH). "
        "3. taraf API'lere, webhook'lara ve REST servislerine bağlanmak için kullanılır. "
        "Örnek: http_request(method='GET', url='https://api.example.com/users')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "description": "HTTP metodu: GET, POST, PUT, DELETE, PATCH",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            },
            "url": {
                "type": "string",
                "description": "İstek gönderilecek URL",
            },
            "headers": {
                "type": "string",
                "description": 'JSON formatında istek header\'ları (opsiyonel). Örn: {"Authorization": "Bearer token"}',
                "default": "",
            },
            "body": {
                "type": "string",
                "description": "İstek gövdesi, JSON string olarak (opsiyonel, POST/PUT/PATCH için)",
                "default": "",
            },
            "timeout": {
                "type": "integer",
                "description": "Zaman aşımı süresi (saniye, varsayılan 10)",
                "default": 10,
            },
        },
        "required": ["method", "url"],
    },
)
def http_request(
    method: str,
    url: str,
    headers: str = "",
    body: str = "",
    timeout: int = 10,
) -> str:
    """Genel HTTP isteği gönderir ve yanıtı döndürür."""
    try:
        import httpx

        # Header'ları parse et
        parsed_headers = {}
        if headers:
            try:
                parsed_headers = json.loads(headers)
            except json.JSONDecodeError:
                return "Hata: headers geçerli JSON formatında değil."

        # Body'yi parse et
        parsed_body = None
        if body:
            try:
                parsed_body = json.loads(body)
                # JSON body gönderilirken Content-Type ekle
                if "content-type" not in {k.lower() for k in parsed_headers}:
                    parsed_headers["Content-Type"] = "application/json"
            except json.JSONDecodeError:
                # JSON değilse raw string gönder
                parsed_body = body

        logger.info(f"http_request: {method} {url}")

        with httpx.Client(timeout=timeout) as client:
            if parsed_body and isinstance(parsed_body, dict):
                response = client.request(method.upper(), url, headers=parsed_headers, json=parsed_body)
            elif parsed_body:
                response = client.request(method.upper(), url, headers=parsed_headers, content=str(parsed_body))
            else:
                response = client.request(method.upper(), url, headers=parsed_headers)

        # Yanıt formatla
        content_type = response.headers.get("content-type", "")
        result = f"HTTP {response.status_code} {response.reason_phrase}\n"
        result += f"URL: {url}\n"
        result += f"Content-Type: {content_type}\n\n"

        # Yanıt gövdesi
        response_text = response.text[:3000]
        if "json" in content_type:
            try:
                parsed = response.json()
                response_text = json.dumps(parsed, indent=2, ensure_ascii=False)[:3000]
            except Exception:
                pass

        result += response_text
        if len(response.text) > 3000:
            result += f"\n\n[... toplam {len(response.text)} karakter, kısaltıldı]"

        return result

    except Exception as e:
        return f"http_request hatası: {str(e)}"

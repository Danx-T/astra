"""
Astra — Web Arama Tool'u.
DuckDuckGo üzerinden ücretsiz web araması yapar (API key gerekmez).
ddgs paketi kullanılır.
"""

from tools.registry import register_tool


@register_tool(
    name="web_search",
    description=(
        "İnternette arama yapar ve sonuçları döndürür. "
        "DuckDuckGo arama motorunu kullanır, API anahtarı gerektirmez. "
        "Sonuçlar başlık, URL ve kısa açıklama içerir. "
        "Örnek: web_search(query='Python FastAPI tutorial')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Aranacak sorgu metni",
            }
        },
        "required": ["query"],
    },
)
def web_search(query: str) -> str:
    """DuckDuckGo ile web araması yapar."""
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

        if not results:
            return f"'{query}' için sonuç bulunamadı."

        # Sonuçları formatla
        output_parts = [f"🔍 '{query}' için arama sonuçları:\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "Başlık yok")
            url = r.get("href", r.get("link", "URL yok"))
            body = r.get("body", r.get("snippet", "Açıklama yok"))
            output_parts.append(f"{i}. **{title}**\n   URL: {url}\n   {body}\n")

        return "\n".join(output_parts)

    except ImportError:
        return "Web arama hatası: 'ddgs' paketi yüklü değil. pip install ddgs"
    except Exception as e:
        return f"Web arama hatası: {str(e)}"

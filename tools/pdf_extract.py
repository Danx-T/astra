"""
Astra — PDF Metin Çıkarma Tool'u.
Workspace içindeki PDF dosyalarından metin çeker.
pdfplumber kütüphanesi kullanılır.
"""

import logging
from tools.registry import register_tool
from tools.file_ops import _safe_resolve

logger = logging.getLogger(__name__)


@register_tool(
    name="pdf_extract",
    description=(
        "Workspace içindeki bir PDF dosyasından metin çıkarır. "
        "Belirli sayfa aralıkları belirtilebilir. "
        "Örnek: pdf_extract(path='rapor.pdf') veya pdf_extract(path='belge.pdf', pages='1-3')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "PDF dosyasının workspace'e göre yolu",
            },
            "pages": {
                "type": "string",
                "description": (
                    "Çıkarılacak sayfalar: '1' (tek sayfa), '1-5' (aralık), "
                    "'' (tümü, varsayılan)"
                ),
                "default": "",
            },
        },
        "required": ["path"],
    },
)
def pdf_extract(path: str, pages: str = "") -> str:
    """PDF dosyasından metin çıkarır."""
    try:
        import pdfplumber
    except ImportError:
        return "Hata: 'pdfplumber' paketi kurulu değil. Çalıştır: pip install pdfplumber"

    try:
        resolved = _safe_resolve(path)
        if not resolved.exists():
            return f"Dosya bulunamadı: {path}"
        if resolved.suffix.lower() != ".pdf":
            return f"Bu bir PDF dosyası değil: {path}"

        with pdfplumber.open(str(resolved)) as pdf:
            total_pages = len(pdf.pages)

            # Sayfa aralığını parse et
            if pages:
                if "-" in pages:
                    parts = pages.split("-", 1)
                    start = max(1, int(parts[0])) - 1
                    end = min(total_pages, int(parts[1]))
                    page_indices = list(range(start, end))
                else:
                    page_num = int(pages) - 1
                    page_indices = [page_num] if 0 <= page_num < total_pages else []
            else:
                page_indices = list(range(min(total_pages, 20)))  # Max 20 sayfa

            if not page_indices:
                return f"Geçersiz sayfa aralığı: '{pages}'. PDF toplam {total_pages} sayfa içeriyor."

            result_parts = [
                f"📄 **{path}** — {total_pages} sayfa\n"
                f"Çıkarılan sayfalar: {page_indices[0]+1}-{page_indices[-1]+1}\n"
            ]

            for i in page_indices:
                page = pdf.pages[i]
                text = page.extract_text() or ""
                result_parts.append(f"\n--- Sayfa {i+1} ---\n{text}")

            full_text = "\n".join(result_parts)

            # Karakter limiti
            if len(full_text) > 8000:
                full_text = full_text[:8000] + f"\n\n[... toplam {len(full_text)} karakter, kısaltıldı]"

            return full_text

    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"PDF okuma hatası: {str(e)}"

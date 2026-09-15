"""
Astra — Dosya İşlemleri Tool'ları.
workspace/ dizini altında güvenli dosya okuma ve yazma.
Path traversal saldırılarına karşı korumalı — workspace dışına erişim engellenir.
"""

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
    # NOT: startswith() güvensizdir (workspace2/ gibi false positive verir)
    # is_relative_to() doğru kontroldür (Python 3.9+)
    workspace_resolved = WORKSPACE_DIR.resolve()
    if not resolved.is_relative_to(workspace_resolved):
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


@register_tool(
    name="append_file",
    description=(
        "Workspace içindeki bir dosyanın sonuna içerik ekler (üzerine yazmaz). "
        "Dosya yoksa yeni oluşturur. "
        "Örnek: append_file(path='log.txt', content='Yeni satır')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Dosyanın workspace'e göre yolu",
            },
            "content": {
                "type": "string",
                "description": "Dosyanın sonuna eklenecek içerik",
            },
        },
        "required": ["path", "content"],
    },
)
def append_file(path: str, content: str) -> str:
    """Workspace altındaki dosyaya ekleme yapar."""
    try:
        resolved = _safe_resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)

        with open(resolved, "a", encoding="utf-8") as f:
            f.write(content)

        total = resolved.stat().st_size
        return f"İçerik eklendi: {path} (eklenen: {len(content)} karakter, toplam: {total} bayt)"

    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Dosya ekleme hatası: {str(e)}"


@register_tool(
    name="list_directory",
    description=(
        "Workspace içindeki bir dizinin içeriğini listeler. "
        "path boş bırakılırsa workspace kökü listelenir. "
        "Örnek: list_directory(path='') veya list_directory(path='proje/src')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Listelenecek dizinin workspace'e göre yolu (boşsa kök)",
                "default": "",
            }
        },
        "required": [],
    },
)
def list_directory(path: str = "") -> str:
    """Workspace altındaki dizin içeriğini listeler."""
    try:
        target = _safe_resolve(path) if path else WORKSPACE_DIR.resolve()

        if not target.exists():
            return f"Dizin bulunamadı: {path}"
        if not target.is_dir():
            return f"Bu bir dizin değil: {path}"

        items = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name))
        if not items:
            return f"📁 {path or 'workspace/'} — boş dizin"

        lines = [f"📁 {path or 'workspace/'} içeriği ({len(items)} öğe):\n"]
        for item in items:
            if item.name.startswith("."):
                continue
            if item.is_dir():
                sub_count = sum(1 for _ in item.iterdir())
                lines.append(f"  📂 {item.name}/  ({sub_count} öğe)")
            else:
                size = item.stat().st_size
                size_str = f"{size:,} B" if size < 1024 else f"{size/1024:.1f} KB"
                lines.append(f"  📄 {item.name}  [{size_str}]")

        return "\n".join(lines)

    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Dizin listeleme hatası: {str(e)}"


@register_tool(
    name="find_files",
    description=(
        "Workspace içinde glob pattern ile dosya arar. "
        "Örnek: find_files(pattern='*.py') veya find_files(pattern='**/*.txt')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob arama pattern'i (örn: '*.py', '**/*.md', 'src/*.js')",
            }
        },
        "required": ["pattern"],
    },
)
def find_files(pattern: str) -> str:
    """Workspace içinde pattern ile dosya arar."""
    try:
        workspace = WORKSPACE_DIR.resolve()
        matches = list(workspace.glob(pattern))

        if not matches:
            return f"'{pattern}' pattern'i için sonuç bulunamadı."

        lines = [f"🔍 '{pattern}' ile {len(matches)} dosya bulundu:\n"]
        for m in sorted(matches)[:50]:
            rel = m.relative_to(workspace)
            if m.is_file():
                size = m.stat().st_size
                size_str = f"{size:,} B" if size < 1024 else f"{size/1024:.1f} KB"
                lines.append(f"  📄 {rel}  [{size_str}]")
            else:
                lines.append(f"  📂 {rel}/")

        if len(matches) > 50:
            lines.append(f"\n  ... ve {len(matches) - 50} dosya daha")

        return "\n".join(lines)

    except Exception as e:
        return f"Dosya arama hatası: {str(e)}"


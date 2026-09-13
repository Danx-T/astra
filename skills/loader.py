"""
Astra — Skill Loader (Yükleyici).
skills/ dizinindeki SKILL.md dosyalarını tarar, frontmatter'dan
name + description okur, ve load_skill tool'unu kayıt eder.
"""

import logging
from pathlib import Path
import yaml
from tools.registry import register_tool
from config import SKILLS_DIR

logger = logging.getLogger(__name__)

# Yüklenen skill'lerin metadata'ları: { "skill_name": { "name", "description", "path" } }
_skills: dict[str, dict] = {}


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    SKILL.md dosyasından YAML frontmatter ve gövdeyi ayırır.

    Returns:
        (frontmatter_dict, body_text)
    """
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
            return frontmatter, body
    return {}, content


def load_all_skills() -> None:
    """
    skills/ dizinindeki tüm SKILL.md dosyalarını tarar ve metadata'larını yükler.
    Başlangıçta bir kez çağrılmalı.
    """
    if not SKILLS_DIR.exists():
        logger.warning(f"Skills dizini bulunamadı: {SKILLS_DIR}")
        return

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        try:
            content = skill_file.read_text(encoding="utf-8")
            frontmatter, body = _parse_frontmatter(content)

            name = frontmatter.get("name", skill_dir.name)
            description = frontmatter.get("description", "Açıklama yok")

            _skills[name] = {
                "name": name,
                "description": description.strip(),
                "path": str(skill_file),
                "content": content,  # Tam içerik (load_skill için)
            }

            logger.info(f"Skill yüklendi: {name}")

        except Exception as e:
            logger.error(f"Skill yükleme hatası ({skill_dir.name}): {e}")


def get_skill_summaries() -> str:
    """
    Tüm skill'lerin name + description özetini döner.
    System prompt'a eklenmek üzere formatlanmış metin.
    """
    if not _skills:
        return "Henüz yüklü skill bulunmuyor."

    lines = ["## Kullanılabilir Skill'ler\n"]
    for skill in _skills.values():
        lines.append(f"- **{skill['name']}**: {skill['description']}")

    lines.append(
        "\nBir skill'in detaylı talimatlarını almak için "
        "`load_skill` tool'unu kullan."
    )
    return "\n".join(lines)


# load_skill tool'unu kayıt et
@register_tool(
    name="load_skill",
    description=(
        "Belirtilen skill'in detaylı talimatlarını yükler. "
        "Skill talimatları, o alanda nasıl çalışılacağına dair "
        "best practice ve adım adım yönergeler içerir. "
        "Mevcut skill'ler: 'research' (araştırma), 'coding_helper' (kod yazma/inceleme)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Yüklenecek skill'in adı (örn: 'research', 'coding_helper')",
            }
        },
        "required": ["name"],
    },
)
def load_skill(name: str) -> str:
    """Belirtilen skill'in tam içeriğini döner."""
    if name not in _skills:
        available = ", ".join(_skills.keys()) if _skills else "hiçbiri"
        return f"Skill bulunamadı: '{name}'. Mevcut skill'ler: {available}"

    skill = _skills[name]
    logger.info(f"Skill yüklendi (tam içerik): {name}")
    return skill["content"]

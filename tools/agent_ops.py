"""
Astra — Agent Yönetim Tool'ları.
Agent'ın kendi kapasitesini sorgulayabilmesi ve ilerideki
multi-agent mimarisi için temel yapı taşları.
"""

import logging
from tools.registry import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="list_tools",
    description=(
        "Şu anda kayıtlı olan tüm tool'ları ve açıklamalarını listeler. "
        "Hangi yeteneklerin mevcut olduğunu öğrenmek için kullan. "
        "Örnek: list_tools()"
    ),
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def list_tools() -> str:
    """Kayıtlı tüm tool'ları listeler."""
    from tools.registry import _registry  # İçeriden registry'ye eriş
    if not _registry:
        return "Hiç kayıtlı tool yok."

    lines = [f"🔧 **Kayıtlı Tool'lar** ({len(_registry)} adet)\n"]
    for name, entry in sorted(_registry.items()):
        desc = entry["schema"]["function"]["description"]
        # Açıklamayı ilk cümleyle sınırla
        short_desc = desc.split(".")[0].strip()
        lines.append(f"- **{name}**: {short_desc}")

    return "\n".join(lines)


@register_tool(
    name="list_skills",
    description=(
        "Yüklü tüm skill'leri ve açıklamalarını listeler. "
        "Hangi uzmanlık alanlarının mevcut olduğunu öğrenmek için kullan. "
        "Skill detayları için load_skill tool'unu kullan. "
        "Örnek: list_skills()"
    ),
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def list_skills() -> str:
    """Yüklü tüm skill'leri listeler."""
    from skills.loader import _skills  # İçeriden skill deposuna eriş
    if not _skills:
        return "Hiç yüklü skill yok."

    lines = [f"💡 **Yüklü Skill'ler** ({len(_skills)} adet)\n"]
    for name, skill in sorted(_skills.items()):
        desc = skill["description"].replace("\n", " ").strip()
        if len(desc) > 120:
            desc = desc[:120] + "..."
        lines.append(f"- **{name}**: {desc}")

    lines.append("\nDetay için: load_skill(name='<skill_adı>')")
    return "\n".join(lines)


@register_tool(
    name="spawn_subagent",
    description=(
        "📌 V5 özelliği — Multi-agent mimarisi için iskelet. "
        "Şu an aktif değil, gelecekte bir alt-agent oluşturup "
        "bağımsız bir görevi çalıştırmasını sağlayacak. "
        "Örnek: spawn_subagent(goal='Şu konuyu araştır: ...')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "goal": {
                "type": "string",
                "description": "Alt-agent'a verilecek hedef/görev açıklaması",
            },
            "tools_allowed": {
                "type": "string",
                "description": "Virgülle ayrılmış izin verilen tool listesi (boşsa tümü)",
                "default": "",
            },
        },
        "required": ["goal"],
    },
)
def spawn_subagent(goal: str, tools_allowed: str = "") -> str:
    """
    [V5 Placeholder] Alt-agent oluşturur.
    Şu an aktif değil — multi-agent mimarisi için yer tutucu.
    """
    logger.info(f"spawn_subagent çağrıldı (placeholder): {goal[:100]}")
    return (
        "⚠️ spawn_subagent henüz aktif değil (V5 özelliği).\n\n"
        f"Hedef: {goal}\n\n"
        "Bu tool ileride bağımsız bir alt-agent başlatıp sonuçlarını "
        "ana agent'a döndürecek. Şimdilik bu görevi mevcut tool'larla "
        "kendin adım adım gerçekleştirmeyi deneyebilirsin."
    )

"""
Astra — Tarih/Saat ve Dönüşüm Tool'ları.
Tarih hesaplama, zaman dilimi, birim dönüştürme gibi
sık kullanılan yardımcı işlemler.
"""

from datetime import datetime, timezone, timedelta
from tools.registry import register_tool


@register_tool(
    name="datetime_now",
    description=(
        "Şu anki tarih ve saati döndürür. Opsiyonel olarak farklı zaman dilimi "
        "ofseti verilebilir (UTC'ye göre saat farkı). "
        "Örnek: datetime_now() veya datetime_now(utc_offset=3) (Türkiye saati)"
    ),
    parameters={
        "type": "object",
        "properties": {
            "utc_offset": {
                "type": "integer",
                "description": "UTC'ye göre saat farkı (Türkiye=3, varsayılan=3)",
                "default": 3,
            },
            "format": {
                "type": "string",
                "description": "Tarih formatı (varsayılan: '%Y-%m-%d %H:%M:%S')",
                "default": "%Y-%m-%d %H:%M:%S",
            },
        },
        "required": [],
    },
)
def datetime_now(utc_offset: int = 3, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Şu anki tarih ve saati döndürür."""
    tz = timezone(timedelta(hours=utc_offset))
    now = datetime.now(tz)

    sign = "+" if utc_offset >= 0 else ""
    return (
        f"🕐 Şu anki zaman (UTC{sign}{utc_offset}):\n"
        f"  {now.strftime(format)}\n"
        f"  Unix timestamp: {int(now.timestamp())}\n"
        f"  ISO format: {now.isoformat()}"
    )


@register_tool(
    name="date_calc",
    description=(
        "Tarih hesaplama yapar: iki tarih arasındaki fark, "
        "bir tarihe gün/hafta/ay ekleme. "
        "Örnek: date_calc(operation='diff', date1='2024-01-15', date2='2024-03-20') "
        "veya date_calc(operation='add', date1='2024-01-15', days=45)"
    ),
    parameters={
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "'diff' (iki tarih farkı) veya 'add' (tarihe gün ekle)",
                "enum": ["diff", "add"],
            },
            "date1": {
                "type": "string",
                "description": "Birinci tarih (YYYY-MM-DD formatı)",
            },
            "date2": {
                "type": "string",
                "description": "İkinci tarih (diff için, YYYY-MM-DD)",
                "default": "",
            },
            "days": {
                "type": "integer",
                "description": "Eklenecek gün sayısı (add için, negatif olabilir)",
                "default": 0,
            },
        },
        "required": ["operation", "date1"],
    },
)
def date_calc(
    operation: str, date1: str, date2: str = "", days: int = 0
) -> str:
    """Tarih hesaplama yapar."""
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")

        if operation == "diff":
            if not date2:
                return "Fark hesabı için date2 gerekli."
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            delta = d2 - d1
            weeks = abs(delta.days) // 7
            months = abs(delta.days) / 30.44  # Ortalama ay uzunluğu
            return (
                f"📅 {date1} → {date2}\n"
                f"  Fark: {delta.days} gün ({weeks} hafta, ~{months:.1f} ay)\n"
                f"  {abs(delta.days)} gün {'sonra' if delta.days > 0 else 'önce'}"
            )

        elif operation == "add":
            result = d1 + timedelta(days=days)
            return (
                f"📅 {date1} + {days} gün = **{result.strftime('%Y-%m-%d')}** "
                f"({result.strftime('%A')})".replace(
                    "Monday", "Pazartesi"
                ).replace(
                    "Tuesday", "Salı"
                ).replace(
                    "Wednesday", "Çarşamba"
                ).replace(
                    "Thursday", "Perşembe"
                ).replace(
                    "Friday", "Cuma"
                ).replace(
                    "Saturday", "Cumartesi"
                ).replace(
                    "Sunday", "Pazar"
                )
            )

        return f"Geçersiz işlem: {operation}"

    except ValueError as e:
        return f"Tarih format hatası: {e}. Beklenen format: YYYY-MM-DD"


@register_tool(
    name="unit_convert",
    description=(
        "Birim dönüştürme: uzunluk, ağırlık, sıcaklık, veri boyutu. "
        "Örnek: unit_convert(value=100, from_unit='km', to_unit='mi') "
        "veya unit_convert(value=36.6, from_unit='celsius', to_unit='fahrenheit')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "Dönüştürülecek değer",
            },
            "from_unit": {
                "type": "string",
                "description": "Kaynak birim",
            },
            "to_unit": {
                "type": "string",
                "description": "Hedef birim",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
)
def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """Birim dönüşümü yapar."""
    from_u = from_unit.lower().strip()
    to_u = to_unit.lower().strip()

    # Sıcaklık (özel formül)
    temp_conversions = {
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
        ("celsius", "kelvin"): lambda v: v + 273.15,
        ("kelvin", "celsius"): lambda v: v - 273.15,
    }

    if (from_u, to_u) in temp_conversions:
        result = temp_conversions[(from_u, to_u)](value)
        return f"🔄 {value} {from_unit} = **{result:.2f} {to_unit}**"

    # Diğer birimler — metre cinsine normalizasyon
    # Uzunluk (metre tabanlı)
    length_to_m = {
        "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
        "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
    }
    # Ağırlık (gram tabanlı)
    weight_to_g = {
        "mg": 0.001, "g": 1, "kg": 1000, "ton": 1_000_000,
        "oz": 28.3495, "lb": 453.592,
    }
    # Veri boyutu (bayt tabanlı)
    data_to_b = {
        "b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4,
        "bit": 0.125,
    }

    for name, table in [("uzunluk", length_to_m), ("ağırlık", weight_to_g), ("veri", data_to_b)]:
        if from_u in table and to_u in table:
            base = value * table[from_u]
            result = base / table[to_u]
            return f"🔄 {value} {from_unit} = **{result:,.6g} {to_unit}**"

    return (
        f"Birim çifti desteklenmiyor: {from_unit} → {to_unit}.\n"
        f"Desteklenen birimler:\n"
        f"  Uzunluk: {', '.join(length_to_m)}\n"
        f"  Ağırlık: {', '.join(weight_to_g)}\n"
        f"  Veri: {', '.join(data_to_b)}\n"
        f"  Sıcaklık: celsius, fahrenheit, kelvin"
    )

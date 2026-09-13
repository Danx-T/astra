"""
Astra — Calculator Tool.
Matematiksel ifadeleri güvenli şekilde hesaplar.
eval() yerine simpleeval kütüphanesi kullanılır (güvenlik).
"""

from simpleeval import simple_eval, InvalidExpression
from tools.registry import register_tool


@register_tool(
    name="calculator",
    description=(
        "Matematiksel ifadeleri güvenli şekilde hesaplar. "
        "Toplama, çıkarma, çarpma, bölme, üs alma gibi temel işlemleri destekler. "
        "Örnek: '125 * 8 + 17', '2 ** 10', '(45 + 55) / 2'"
    ),
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Hesaplanacak matematiksel ifade (örn: '125 * 8 + 17')",
            }
        },
        "required": ["expression"],
    },
)
def calculator(expression: str) -> str:
    """Verilen matematik ifadesini güvenli şekilde hesaplar."""
    try:
        # simpleeval ile güvenli hesaplama — eval() kullanmıyoruz
        result = simple_eval(expression)
        return f"{expression} = {result}"
    except InvalidExpression as e:
        return f"Geçersiz ifade: {e}"
    except Exception as e:
        return f"Hesaplama hatası: {str(e)}"

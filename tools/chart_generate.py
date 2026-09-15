"""
Astra — Grafik Üretme Tool'u.
CSV verisinden veya JSON verisinden matplotlib ile grafik üretir
ve workspace'e PNG olarak kaydeder.
"""

import json
import logging
from tools.registry import register_tool
from tools.file_ops import _safe_resolve
from config import WORKSPACE_DIR

logger = logging.getLogger(__name__)


@register_tool(
    name="chart_generate",
    description=(
        "Sayısal veriden grafik üretir ve workspace'e PNG olarak kaydeder. "
        "Desteklenen grafik tipleri: line, bar, pie, scatter, histogram. "
        "Veri JSON formatında verilir. "
        "Örnek: chart_generate(data_json='{\"x\": [1,2,3], \"y\": [10,20,15]}', "
        "chart_type='line', title='Satış Grafiği', output_filename='satis.png')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "data_json": {
                "type": "string",
                "description": (
                    "JSON formatında veri. Formatlar:\n"
                    "- Line/Bar/Scatter: '{\"x\": [...], \"y\": [...]}'\n"
                    "- Pie: '{\"labels\": [...], \"values\": [...]}'\n"
                    "- Histogram: '{\"values\": [...]}'"
                ),
            },
            "chart_type": {
                "type": "string",
                "description": "Grafik tipi: line, bar, pie, scatter, histogram",
                "enum": ["line", "bar", "pie", "scatter", "histogram"],
            },
            "title": {
                "type": "string",
                "description": "Grafik başlığı",
                "default": "Grafik",
            },
            "output_filename": {
                "type": "string",
                "description": "Kaydedilecek PNG dosyasının adı (workspace/ altına)",
                "default": "chart.png",
            },
            "xlabel": {
                "type": "string",
                "description": "X ekseni etiketi (opsiyonel)",
                "default": "",
            },
            "ylabel": {
                "type": "string",
                "description": "Y ekseni etiketi (opsiyonel)",
                "default": "",
            },
        },
        "required": ["data_json", "chart_type", "output_filename"],
    },
)
def chart_generate(
    data_json: str,
    chart_type: str,
    output_filename: str,
    title: str = "Grafik",
    xlabel: str = "",
    ylabel: str = "",
) -> str:
    """Veriden grafik üretir ve workspace'e PNG kaydeder."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # Headless mod (GUI penceresi açma)
        import matplotlib.pyplot as plt
    except ImportError:
        return "Hata: 'matplotlib' paketi kurulu değil. Çalıştır: pip install matplotlib"

    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        return f"Geçersiz JSON verisi: {e}"

    try:
        output_path = _safe_resolve(output_filename)
        if not output_filename.lower().endswith(".png"):
            output_filename = output_filename + ".png"
            output_path = _safe_resolve(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Grafik stil ayarları
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#1a1a2e")
        ax.set_facecolor("#12121a")

        colors = ["#7c5cfc", "#a78bfa", "#34d399", "#fbbf24", "#f87171"]

        if chart_type == "line":
            x = data.get("x", list(range(len(data.get("y", [])))))
            y = data.get("y", [])
            ax.plot(x, y, color=colors[0], linewidth=2, marker="o", markersize=4)
            ax.fill_between(x, y, alpha=0.15, color=colors[0])

        elif chart_type == "bar":
            x = data.get("x", list(range(len(data.get("y", [])))))
            y = data.get("y", [])
            bars = ax.bar(x, y, color=colors[0], alpha=0.85, edgecolor=colors[1], linewidth=0.5)
            for bar in bars:
                bar.set_color(colors[0])

        elif chart_type == "pie":
            labels = data.get("labels", [])
            values = data.get("values", [])
            ax.pie(
                values, labels=labels, autopct="%1.1f%%",
                colors=colors[:len(values)],
                startangle=90, pctdistance=0.85,
            )
            ax.axis("equal")

        elif chart_type == "scatter":
            x = data.get("x", [])
            y = data.get("y", [])
            ax.scatter(x, y, color=colors[0], alpha=0.7, s=60, edgecolors=colors[1], linewidth=0.5)

        elif chart_type == "histogram":
            values = data.get("values", [])
            bins = data.get("bins", 20)
            ax.hist(values, bins=bins, color=colors[0], alpha=0.85, edgecolor=colors[1], linewidth=0.5)

        # Etiketler
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color="#e8e8ed")
        if xlabel:
            ax.set_xlabel(xlabel, color="#8e8ea0")
        if ylabel:
            ax.set_ylabel(ylabel, color="#8e8ea0")

        ax.tick_params(colors="#8e8ea0")
        ax.spines["bottom"].set_color("#2a2a3e")
        ax.spines["left"].set_color("#2a2a3e")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.1, color="#ffffff")

        plt.tight_layout()
        plt.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)

        size_kb = output_path.stat().st_size / 1024
        return (
            f"✅ Grafik oluşturuldu: workspace/{output_filename} ({size_kb:.1f} KB)\n"
            f"Tip: {chart_type}, Başlık: {title}"
        )

    except ValueError as e:
        plt.close("all")
        return str(e)
    except Exception as e:
        plt.close("all")
        return f"Grafik oluşturma hatası: {str(e)}"

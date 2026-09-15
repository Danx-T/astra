"""
Astra — Veri İşleme Tool'ları.
CSV okuma/filtreleme/özet, dosya diff, veri istatistikleri.
Pandas bağımlılığı yoktur; stdlib csv + difflib kullanılır.
"""

import csv
import json
import difflib
from tools.registry import register_tool
from tools.file_ops import _safe_resolve


@register_tool(
    name="csv_query",
    description=(
        "Workspace içindeki bir CSV dosyasını okur; isteğe bağlı olarak "
        "belirli sütunlara göre filtreler ve satırları döndürür. "
        "Örnek: csv_query(path='data.csv', filter_col='city', filter_val='Istanbul', columns='name,age')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "CSV dosyasının workspace'e göre yolu",
            },
            "filter_col": {
                "type": "string",
                "description": "Filtrelenecek sütun adı (opsiyonel)",
                "default": "",
            },
            "filter_val": {
                "type": "string",
                "description": "Filtrelenecek değer (opsiyonel)",
                "default": "",
            },
            "columns": {
                "type": "string",
                "description": "Gösterilecek sütunlar, virgülle ayrılmış (opsiyonel, boşsa hepsi)",
                "default": "",
            },
            "max_rows": {
                "type": "integer",
                "description": "Döndürülecek maksimum satır sayısı (varsayılan 50)",
                "default": 50,
            },
        },
        "required": ["path"],
    },
)
def csv_query(
    path: str,
    filter_col: str = "",
    filter_val: str = "",
    columns: str = "",
    max_rows: int = 50,
) -> str:
    """CSV dosyasını okur, filtreler ve formatlanmış sonuç döndürür."""
    try:
        resolved = _safe_resolve(path)
        if not resolved.exists():
            return f"Dosya bulunamadı: {path}"

        selected_cols = [c.strip() for c in columns.split(",") if c.strip()] if columns else []
        rows = []
        headers = []

        with open(resolved, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

            # Sütun seçimi doğrula
            if selected_cols:
                invalid = [c for c in selected_cols if c not in headers]
                if invalid:
                    return f"Geçersiz sütun(lar): {invalid}. Mevcut sütunlar: {headers}"

            for row in reader:
                # Filtre uygula
                if filter_col and filter_val:
                    if filter_col not in row:
                        return f"Filtre sütunu bulunamadı: '{filter_col}'. Mevcut: {headers}"
                    if filter_val.lower() not in str(row[filter_col]).lower():
                        continue

                # Sütun seçimi
                if selected_cols:
                    rows.append({c: row[c] for c in selected_cols})
                else:
                    rows.append(dict(row))

                if len(rows) >= max_rows:
                    break

        if not rows:
            return f"Sonuç bulunamadı. (Filtre: {filter_col}={filter_val})"

        # Tablo formatında çıktı
        display_cols = selected_cols if selected_cols else (headers or [])
        col_widths = {c: max(len(c), max((len(str(r.get(c, ""))) for r in rows), default=0)) for c in display_cols}

        header_line = " | ".join(c.ljust(col_widths[c]) for c in display_cols)
        sep_line = "-+-".join("-" * col_widths[c] for c in display_cols)
        data_lines = [
            " | ".join(str(r.get(c, "")).ljust(col_widths[c]) for c in display_cols)
            for r in rows
        ]

        result = f"📊 {path} — {len(rows)} satır\n\n"
        result += header_line + "\n" + sep_line + "\n" + "\n".join(data_lines)
        return result

    except Exception as e:
        return f"CSV okuma hatası: {str(e)}"


@register_tool(
    name="data_summary",
    description=(
        "Workspace içindeki CSV veya JSON dosyasının istatistiksel özetini çıkarır: "
        "satır sayısı, sütunlar, sayısal sütunlar için min/max/ortalama. "
        "Örnek: data_summary(path='sales.csv')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "CSV veya JSON dosyasının workspace'e göre yolu",
            }
        },
        "required": ["path"],
    },
)
def data_summary(path: str) -> str:
    """CSV veya JSON dosyasının özet istatistiklerini döndürür."""
    try:
        resolved = _safe_resolve(path)
        if not resolved.exists():
            return f"Dosya bulunamadı: {path}"

        suffix = resolved.suffix.lower()

        if suffix == ".csv":
            rows = []
            with open(resolved, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                for row in reader:
                    rows.append(row)

            if not rows:
                return f"{path}: Boş CSV dosyası."

            lines = [f"📊 **{path}** özeti", f"- Satır sayısı: {len(rows)}", f"- Sütun sayısı: {len(headers)}", f"- Sütunlar: {', '.join(headers)}", ""]

            # Sayısal sütunlar için istatistik
            for col in headers:
                values = []
                for row in rows:
                    try:
                        values.append(float(row[col]))
                    except (ValueError, TypeError):
                        pass
                if len(values) > len(rows) * 0.5:  # Çoğunluğu sayısal ise
                    lines.append(
                        f"- **{col}**: min={min(values):.2f}, max={max(values):.2f}, "
                        f"ort={sum(values)/len(values):.2f}"
                    )
            return "\n".join(lines)

        elif suffix == ".json":
            with open(resolved, encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                lines = [f"📊 **{path}** özeti", f"- Eleman sayısı: {len(data)}"]
                if data and isinstance(data[0], dict):
                    lines.append(f"- Anahtarlar: {', '.join(data[0].keys())}")
                return "\n".join(lines)
            elif isinstance(data, dict):
                return f"📊 **{path}**: JSON objesi, {len(data)} anahtar: {', '.join(list(data.keys())[:20])}"
            else:
                return f"📊 **{path}**: {type(data).__name__} tipinde veri"

        else:
            return f"Desteklenmeyen format: {suffix}. Desteklenenler: .csv, .json"

    except Exception as e:
        return f"Veri özeti hatası: {str(e)}"


@register_tool(
    name="diff_files",
    description=(
        "Workspace içindeki iki dosyayı satır satır karşılaştırır ve farkları gösterir. "
        "Örnek: diff_files(path1='v1.py', path2='v2.py')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path1": {
                "type": "string",
                "description": "İlk dosyanın workspace'e göre yolu",
            },
            "path2": {
                "type": "string",
                "description": "İkinci dosyanın workspace'e göre yolu",
            },
        },
        "required": ["path1", "path2"],
    },
)
def diff_files(path1: str, path2: str) -> str:
    """İki dosyayı karşılaştırır, unified diff formatında farkları döndürür."""
    try:
        r1 = _safe_resolve(path1)
        r2 = _safe_resolve(path2)

        if not r1.exists():
            return f"Dosya bulunamadı: {path1}"
        if not r2.exists():
            return f"Dosya bulunamadı: {path2}"

        lines1 = r1.read_text(encoding="utf-8").splitlines()
        lines2 = r2.read_text(encoding="utf-8").splitlines()

        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile=path1,
            tofile=path2,
        ))

        if not diff:
            return f"✅ '{path1}' ve '{path2}' aynı — fark yok."

        return f"📝 Diff ({len(diff)} satır değişiklik):\n\n" + "\n".join(diff[:200])

    except Exception as e:
        return f"Diff hatası: {str(e)}"

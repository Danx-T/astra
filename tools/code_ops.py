"""
Astra — Kod Çalıştırma ve Geliştirme Tool'ları.
run_python: güvenli subprocess sandbox
run_shell: kısıtlı shell komut seti
git_ops: temel git işlemleri
lint_code: pylint entegrasyonu
format_code: black entegrasyonu
"""

import subprocess
import logging
import sys
import shlex
from pathlib import Path
from tools.registry import register_tool
from tools.file_ops import _safe_resolve
from config import WORKSPACE_DIR

logger = logging.getLogger(__name__)

# --- Güvenli shell komut listesi ---
ALLOWED_SHELL_COMMANDS = {
    "echo", "python", "python3", "pip", "pip3",
    "ls", "dir", "cat", "type", "head", "tail",
    "mkdir", "touch", "pwd", "cd",
    "git", "black", "pylint", "flake8",
    "node", "npm", "yarn",
}


def _run_subprocess(cmd: list[str], cwd: str, timeout: int = 15) -> str:
    """Komutu subprocess'te çalıştırır, stdout+stderr döndürür."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )
    output = ""
    if result.stdout:
        output += result.stdout
    if result.stderr:
        output += "\n[STDERR]\n" + result.stderr if output else result.stderr

    return output.strip() or "(Çıktı yok)"


@register_tool(
    name="run_python",
    description=(
        "Python kodunu izole bir subprocess'te çalıştırır ve çıktısını döndürür. "
        "Kod ayrı bir Python process'inde çalışır (güvenli). "
        "Çalışma dizini workspace/ olarak ayarlanır. "
        "Örnek: run_python(code='print(2 ** 10)')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Çalıştırılacak Python kodu",
            },
            "timeout": {
                "type": "integer",
                "description": "Zaman aşımı saniye (varsayılan 10)",
                "default": 10,
            },
        },
        "required": ["code"],
    },
)
def run_python(code: str, timeout: int = 10) -> str:
    """Python kodunu güvenli subprocess'te çalıştırır."""
    try:
        logger.info(f"run_python: {code[:100]}...")

        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(WORKSPACE_DIR),
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n[HATA/UYARI]\n" if output else "") + result.stderr

        exit_info = f"\n[Çıkış kodu: {result.returncode}]"
        return (output.strip() or "(Çıktı yok)") + exit_info

    except subprocess.TimeoutExpired:
        return f"Zaman aşımı: Kod {timeout} saniye içinde tamamlanamadı."
    except Exception as e:
        return f"run_python hatası: {str(e)}"


@register_tool(
    name="run_shell",
    description=(
        "Kısıtlı bir shell komutu çalıştırır. "
        "Güvenlik: yalnızca onaylı komutlar çalıştırılabilir "
        "(python, git, pip, echo, ls/dir, black, pylint vs.). "
        "Çalışma dizini workspace/ olarak ayarlanır. "
        "Örnek: run_shell(command='python script.py') veya run_shell(command='git status')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Çalıştırılacak shell komutu",
            },
            "timeout": {
                "type": "integer",
                "description": "Zaman aşımı saniye (varsayılan 15)",
                "default": 15,
            },
        },
        "required": ["command"],
    },
)
def run_shell(command: str, timeout: int = 15) -> str:
    """Kısıtlı shell komutu çalıştırır."""
    try:
        # Komutu parse et ve izin kontrolü yap
        parts = shlex.split(command, posix=False)
        if not parts:
            return "Boş komut."

        base_cmd = Path(parts[0]).stem.lower()  # Sadece dosya adı (yol olmadan)
        if base_cmd not in ALLOWED_SHELL_COMMANDS:
            return (
                f"Güvenlik: '{parts[0]}' komutuna izin verilmiyor. "
                f"İzin verilenler: {', '.join(sorted(ALLOWED_SHELL_COMMANDS))}"
            )

        logger.info(f"run_shell: {command}")
        return _run_subprocess(parts, cwd=str(WORKSPACE_DIR), timeout=timeout)

    except subprocess.TimeoutExpired:
        return f"Zaman aşımı: Komut {timeout} saniye içinde tamamlanamadı."
    except Exception as e:
        return f"run_shell hatası: {str(e)}"


@register_tool(
    name="git_ops",
    description=(
        "Workspace dizininde temel git işlemleri yapar. "
        "Desteklenen eylemler: status, diff, log, init, add, commit. "
        "Örnek: git_ops(action='status') veya git_ops(action='commit', args='-m \"ilk commit\"')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Git eylemi",
                "enum": ["status", "diff", "log", "init", "add", "commit", "branch", "show"],
            },
            "args": {
                "type": "string",
                "description": "Ek git argümanları (opsiyonel). Örn: '-m \"mesaj\"' veya '--oneline -5'",
                "default": "",
            },
        },
        "required": ["action"],
    },
)
def git_ops(action: str, args: str = "") -> str:
    """Workspace içinde git işlemi çalıştırır."""
    try:
        ALLOWED_ACTIONS = {"status", "diff", "log", "init", "add", "commit", "branch", "show"}
        if action not in ALLOWED_ACTIONS:
            return f"Geçersiz git eylemi: '{action}'. İzin verilenler: {ALLOWED_ACTIONS}"

        cmd = ["git", action]
        if args:
            cmd.extend(shlex.split(args, posix=False))

        logger.info(f"git_ops: {' '.join(cmd)}")
        return _run_subprocess(cmd, cwd=str(WORKSPACE_DIR), timeout=20)

    except subprocess.TimeoutExpired:
        return "Zaman aşımı: git komutu 20 saniye içinde tamamlanamadı."
    except Exception as e:
        return f"git_ops hatası: {str(e)}"


@register_tool(
    name="lint_code",
    description=(
        "Workspace içindeki bir Python dosyasını pylint ile analiz eder. "
        "Kod kalite sorunları, PEP8 ihlalleri ve olası hataları raporlar. "
        "Örnek: lint_code(path='script.py')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Analiz edilecek Python dosyasının workspace'e göre yolu",
            }
        },
        "required": ["path"],
    },
)
def lint_code(path: str) -> str:
    """Pylint ile kod kalite analizi yapar."""
    try:
        resolved = _safe_resolve(path)
        if not resolved.exists():
            return f"Dosya bulunamadı: {path}"

        result = subprocess.run(
            [sys.executable, "-m", "pylint", str(resolved), "--score=yes", "--output-format=text"],
            capture_output=True, text=True, timeout=30,
        )

        output = (result.stdout + result.stderr).strip()
        if not output:
            return "pylint çıktı üretmedi. Kurulu mu kontrol et: pip install pylint"
        return f"🔍 **{path}** lint raporu:\n\n{output}"

    except FileNotFoundError:
        return "pylint bulunamadı. Kur: pip install pylint"
    except subprocess.TimeoutExpired:
        return "Zaman aşımı: lint analizi 30 saniyeyi aştı."
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"lint_code hatası: {str(e)}"


@register_tool(
    name="format_code",
    description=(
        "Workspace içindeki bir Python dosyasını black ile formatlar (PEP8 uyumlu). "
        "Dosyayı yerinde değiştirir ve hangi değişikliklerin yapıldığını raporlar. "
        "Örnek: format_code(path='script.py')"
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Formatlanacak Python dosyasının workspace'e göre yolu",
            }
        },
        "required": ["path"],
    },
)
def format_code(path: str) -> str:
    """Black ile Python kodunu formatlar."""
    try:
        resolved = _safe_resolve(path)
        if not resolved.exists():
            return f"Dosya bulunamadı: {path}"

        # Önce --check ile değişiklik gerekip gerekmediğini kontrol et
        check_result = subprocess.run(
            [sys.executable, "-m", "black", str(resolved), "--check", "--quiet"],
            capture_output=True, text=True, timeout=30,
        )

        if "No module named" in check_result.stderr:
            return "black bulunamadı. Kur: pip install black"

        if check_result.returncode == 0:
            # Zaten düzgün formatlanmış
            return f"✅ **{path}** zaten düzgün formatlanmış — değişiklik yok."

        # Değişiklik gerekiyor — formatla
        format_result = subprocess.run(
            [sys.executable, "-m", "black", str(resolved)],
            capture_output=True, text=True, timeout=30,
        )

        if format_result.returncode == 0:
            return f"✅ **{path}** başarıyla formatlandı (black)."

        output = (format_result.stdout + format_result.stderr).strip()
        return f"⚠️ black hatası:\n{output}"

    except subprocess.TimeoutExpired:
        return "Zaman aşımı: format işlemi 30 saniyeyi aştı."
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"format_code hatası: {str(e)}"

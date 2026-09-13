"""
Astra — Merkezi Konfigürasyon Modülü.
Tüm ayarlar .env dosyasından okunur; hardcode değer kullanılmaz.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent

# --- Groq / LLM Ayarları ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))

# --- Agent Ayarları ---
MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))

# --- Workspace (tool sandbox dizini) ---
WORKSPACE_DIR: Path = BASE_DIR / os.getenv("WORKSPACE_DIR", "workspace")
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

# --- Veritabanı ---
DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'agent.db'}"

# --- Skills dizini ---
SKILLS_DIR: Path = BASE_DIR / "skills"

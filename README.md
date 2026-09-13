# ✦ Astra — Mini AI Agent Platform (MVP)

**LLM + Tools + Skills + Memory + Agent Loop** mimarisine sahip, genişletilebilir bir AI agent platformu.

## 🚀 Hızlı Başlangıç

### 1. Gereksinimleri Kur
```bash
pip install -r requirements.txt
```

### 2. API Key Ayarla
`.env.example` dosyasını `.env` olarak kopyala ve Groq API key'ini gir:
```bash
cp .env.example .env
# .env dosyasını düzenle: GROQ_API_KEY=gsk_xxxxxxxx
```

### 3. Çalıştır
```bash
uvicorn main:app --reload
```

### 4. Aç
Tarayıcıda [http://localhost:8000](http://localhost:8000) adresine git.

---

## 🏗️ Mimari

```
astra/
├── main.py                 # FastAPI app + endpoint'ler
├── config.py               # Merkezi konfigürasyon (.env okur)
├── llm/
│   └── client.py           # GroqCloud API istemcisi (OpenAI SDK)
├── tools/
│   ├── registry.py         # Tool kayıt sistemi (@register_tool)
│   ├── calculator.py       # Güvenli matematik hesaplama (simpleeval)
│   ├── file_ops.py         # Dosya okuma/yazma (workspace sandbox)
│   └── web_search.py       # DuckDuckGo web araması
├── skills/
│   ├── loader.py           # Skill yükleyici + load_skill tool
│   ├── research/SKILL.md   # Araştırma skill'i
│   └── coding_helper/SKILL.md  # Kod yazma skill'i
├── memory/
│   ├── models.py           # SQLAlchemy modelleri (SQLite)
│   └── store.py            # Conversation/message CRUD
├── agent/
│   └── loop.py             # Ana agent döngüsü (tool calling loop)
├── workspace/              # Tool'ların dosya sandbox'ı
└── static/
    └── index.html          # Chat arayüzü
```

### Bileşenler

| Bileşen | Açıklama |
|---------|----------|
| **LLM Katmanı** | GroqCloud API'sine OpenAI SDK ile bağlanır. Tool calling destekler. |
| **Tools** | Decorator tabanlı registry. Her tool ayrı dosyada, otomatik LLM entegrasyonu. |
| **Skills** | SKILL.md formatında talimat dosyaları. LLM gerektiğinde `load_skill` ile yükler. |
| **Memory** | SQLite ile kalıcı konuşma geçmişi. Her mesaj DB'ye kaydedilir. |
| **Agent Loop** | İteratif tool calling döngüsü. LLM → tool çağır → sonucu geri gönder → tekrar sor. |

### Agent Loop Akışı

```
Kullanıcı mesajı
     ↓
DB'ye kaydet + history çek
     ↓
System prompt oluştur (tool'lar + skill'ler)
     ↓
┌─── LLM'i çağır ←──────────────────┐
│         ↓                          │
│   Tool call var mı?               │
│     ├── EVET → Tool'u çalıştır    │
│     │         Sonucu DB'ye kaydet  │
│     │         Loop'a devam ────────┘
│     └── HAYIR → Final cevap
│                 DB'ye kaydet
│                 Kullanıcıya döndür
└──────────────────────────────────────
```

---

## 🔧 Yeni Tool Ekleme

1. `tools/` altına yeni bir dosya oluştur (örn: `tools/translator.py`)
2. `@register_tool` decorator'ünü kullan:

```python
from tools.registry import register_tool

@register_tool(
    name="translate",
    description="Metni çevirir",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Çevrilecek metin"},
            "target_lang": {"type": "string", "description": "Hedef dil"}
        },
        "required": ["text", "target_lang"]
    }
)
def translate(text: str, target_lang: str) -> str:
    # Çeviri mantığı
    return f"Çeviri: ..."
```

3. `main.py`'deki lifespan fonksiyonuna import ekle:
```python
import tools.translator  # noqa: F401
```

**Bu kadar!** `agent/loop.py`'ye dokunmana gerek yok.

---

## 📚 Yeni Skill Ekleme

1. `skills/<skill_adi>/SKILL.md` dosyası oluştur
2. YAML frontmatter ekle:

```markdown
---
name: my_skill
description: Bu skill şunu yapar...
---

# Skill Talimatları
...
```

Uygulama başlangıcında otomatik olarak yüklenir.

---

## 🔌 API Endpoint'leri

| Method | Yol | Açıklama |
|--------|-----|----------|
| `GET` | `/` | Chat arayüzü |
| `POST` | `/conversations` | Yeni conversation oluştur |
| `GET` | `/conversations` | Tüm conversation'ları listele |
| `GET` | `/conversations/{id}/messages` | Mesaj geçmişini getir |
| `POST` | `/conversations/{id}/message` | Mesaj gönder (agent loop çalışır) |

---

## ⚙️ Konfigürasyon (.env)

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `GROQ_API_KEY` | - | Groq API anahtarı (zorunlu) |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | API base URL |
| `LLM_MODEL` | `openai/gpt-oss-120b` | Kullanılacak model |
| `LLM_TEMPERATURE` | `0.7` | Yaratıcılık parametresi |
| `LLM_MAX_TOKENS` | `4096` | Maksimum token sayısı |
| `MAX_AGENT_ITERATIONS` | `10` | Agent loop max iterasyon |
| `WORKSPACE_DIR` | `workspace` | Tool sandbox dizini |

---

## 🛡️ Güvenlik Notları

- **eval() kullanılmaz** — matematik için `simpleeval` kütüphanesi kullanılır.
- **Path traversal koruması** — dosya tool'ları workspace dışına erişemez.
- **Hata yönetimi** — tool hataları agent loop'u çökertmez, LLM'e hata mesajı döner.

---

## 📋 Lisans

Bu proje bir MVP/öğrenme projesidir. İstediğiniz gibi kullanabilirsiniz.

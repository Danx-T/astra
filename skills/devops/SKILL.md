---
name: devops
description: >
  Deployment, CI/CD, container ve monitoring temelleri.
  Uygulama dağıtımı, süreç otomasyonu, altyapı yönetimi ve
  gözlemlenebilirlik (observability) konularında rehberlik.
---

# ⚙️ DevOps Skill — Dağıtım ve Otomasyon Rehberi

## Amaç
Uygulamaları güvenilir, tekrarlanabilir ve izlenebilir şekilde dağıtmak ve yönetmek.

## Talimatlar

### 1. Deployment Hazırlığı
Her deployment öncesi kontrol listesi:
- [ ] Bağımlılıklar `requirements.txt` / `package.json`'a eklenmiş mi?
- [ ] Ortam değişkenleri `.env.example`'da belgelenmiş mi?
- [ ] Gizli bilgiler (API key, parola) kod içinde değil mi?
- [ ] Temel testler geçiyor mu?
- [ ] Sürüm numarası güncellendi mi?

### 2. Dockerization
**Basit Dockerfile (Python):**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: "3.9"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./workspace:/app/workspace
```

### 3. CI/CD (GitHub Actions Örneği)
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v
      - name: Deploy
        run: echo "Deploy adımı buraya"
```

### 4. Environment Yönetimi
| Ortam | Amaç | Dikkat |
|-------|------|--------|
| **development** | Yerel geliştirme | Hata mesajları açık, hot-reload |
| **staging** | Test ortamı | Production'a yakın, test verisi |
| **production** | Canlı | Hata mesajları gizli, optimize |

### 5. Monitoring ve Loglama
- **Yapılandırılmış log**: JSON formatında logla (makine okunabilir).
- **Log seviyeleri**: DEBUG → INFO → WARNING → ERROR → CRITICAL.
- **Metrikler**: Request/s, yanıt süresi, hata oranı.
- **Sağlık endpoint'i**: `GET /health` ekle:
  ```python
  @app.get("/health")
  def health_check():
      return {"status": "ok", "version": "0.1.0"}
  ```

### 6. Astra Özelinde
- **SQLite → PostgreSQL geçişi**: `DATABASE_URL` değiştirmek yeterli (SQLAlchemy).
- **Ölçekleme**: Birden fazla uvicorn worker: `uvicorn main:app --workers 4`.
- **Reverse proxy**: Nginx ile HTTPS + rate limiting.
- **Yedekleme**: `agent.db` dosyasını düzenli yedekle.

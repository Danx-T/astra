---
name: web_scraping
description: >
  web_fetch tool'u ile web içeriği çekme, veri ayıklama ve
  etik web kazıma uygulamaları. Rate-limit, robots.txt ve
  yasal uyum konularında rehber.
---

# 🕷️ Web Scraping Skill — Web Veri Çekme Rehberi

## Amaç
Web sitelerinden etik ve verimli şekilde veri toplamak.

## Talimatlar

### 1. Önce Araştır
- `web_search` ile hedef siteyi bul.
- `web_fetch` ile URL içeriğini çek:
  ```
  web_fetch(url='https://site.com/data', max_chars=8000)
  ```

### 2. Hangi Tool Kullanılır?
| İhtiyaç | Tool |
|---------|------|
| Hızlı özet, snippet | `web_search` |
| Sayfanın tam metni | `web_fetch` |
| API endpoint | `http_request` |
| Çoklu sayfa | `web_fetch` + döngü mantığı |

### 3. Verimli Çekme
- **Sayfalama**: `/page=1`, `/page=2` URL pattern'ini dene.
- **max_chars ayarla**: Sadece ihtiyacın kadar çek.
- **Yapısal URL'ler**: Veri genellikle `/api/`, `/data/`, `/json/` altında.

### 4. Veri Ayıklama
`web_fetch` düz metin döndürür. Verileri ayıklamak için:
- `run_python` ile regex veya string işleme yap:
  ```python
  import re
  text = """... web_fetch çıktısı ..."""
  prices = re.findall(r'\$[\d,]+\.?\d*', text)
  print(prices)
  ```
- Çıktıyı `write_file` ile CSV/JSON olarak kaydet.

### 5. Rate-Limit ve Etik Kurallar
- **İki istek arası bek**: Yoğun kazımada `run_python` ile `time.sleep(1)`.
- **robots.txt kontrol et**: `web_fetch(url='https://site.com/robots.txt')`
- **Kullanım şartlarına uy**: Ticari kullanım için site politikasını oku.
- **Kişisel veri**: GDPR/KVKK — kişisel verileri saklamaktan kaçın.

### 6. Yasal ve Güvenilir Alternatifler
- Resmi **API** varsa her zaman tercih et (daha stabil, etik).
- **Açık veri portalları**: data.gov.tr, opendata.ibb.gov.tr, Kaggle.
- **RSS/Atom**: Haber siteleri için ideal.

### 7. Hata Yönetimi
- 403 → Site botu engelliyor, farklı User-Agent veya API ara.
- 429 → Rate limit, daha yavaş git.
- 404 → URL değişmiş, `web_search` ile yeni URL bul.
- Boş içerik → JavaScript ile yüklenen site (web_fetch JS çalıştırmaz).

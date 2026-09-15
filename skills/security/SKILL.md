---
name: security
description: >
  Uygulama güvenliği, yaygın güvenlik açıkları ve güvenli kod yazma rehberi.
  OWASP Top 10, Python güvenliği, API güvenliği ve veri koruma konularını kapsar.
---

# 🛡️ Security Skill — Güvenlik Rehberi

## Amaç
Güvenli kod yazmak, yaygın güvenlik açıklarını tanımak ve önlemek.

## Talimatlar

### 1. OWASP Top 10 Kontrol Listesi
Her kod incelemesinde şunları kontrol et:

| # | Açık | Kontrol |
|---|------|---------|
| 1 | Injection (SQL, OS, LDAP) | Kullanıcı girdisi parametrize ediliyor mu? |
| 2 | Broken Authentication | Oturum yönetimi güvenli mi? |
| 3 | Sensitive Data Exposure | Hassas veriler şifreli mi? |
| 4 | XXE | XML parser güvenli mi? |
| 5 | Broken Access Control | Yetki kontrolleri var mı? |
| 6 | Security Misconfiguration | Varsayılan ayarlar değiştirilmiş mi? |
| 7 | XSS | Çıktılar escape ediliyor mu? |
| 8 | Insecure Deserialization | pickle/eval kullanılıyor mu? |
| 9 | Known Vulnerabilities | Bağımlılıklar güncel mi? |
| 10 | Insufficient Logging | Güvenlik olayları loglanıyor mu? |

### 2. Python Güvenlik Kuralları
```python
# ✗ TEHLİKELİ
eval(user_input)
exec(user_code)
os.system(f"cmd {user_input}")
pickle.loads(untrusted_data)
yaml.load(data)  # unsafe loader

# ✓ GÜVENLİ
simpleeval.simple_eval(user_input)
subprocess.run(["cmd", user_input], shell=False)
json.loads(data)
yaml.safe_load(data)
```

### 3. API Güvenliği
- **Rate limiting**: Aşırı istekleri sınırla.
- **Input validation**: Tüm girdileri doğrula (tip, uzunluk, format).
- **HTTPS**: Tüm iletişim şifreli olmalı.
- **CORS**: Sadece gerekli origin'lere izin ver.
- **API Key yönetimi**: `.env` kullan, koda gömme, git'e commit'leme.

### 4. Veri Güvenliği
- Parolalar: `bcrypt` veya `argon2` ile hash'le.
- Hassas veriler: Loglama, hata mesajlarında gösterme.
- Yedekleme: Veritabanını düzenli yedekle.
- KVKK/GDPR: Kişisel verileri sadece gerektiği kadar sakla.

### 5. Güvenlik Test Araçları
- `bandit` — Python güvenlik tarayıcısı
- `safety` — bağımlılık güvenlik kontrolü
- `npm audit` — Node.js bağımlılık kontrolü
- `sqlmap` — SQL injection test
- `OWASP ZAP` — web uygulama tarayıcı

### 6. Best Practices
- **Principle of Least Privilege**: Minimum gerekli yetki ver.
- **Defense in Depth**: Tek savunma katmanına güvenme.
- **Fail Secure**: Hata durumunda güvenli tarafa düş.
- **Security by Default**: Varsayılan ayarlar güvenli olsun.

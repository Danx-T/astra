---
name: code_review
description: >
  Kod inceleme, PR analizi ve kod kalitesi değerlendirmesi.
  Güvenlik açıkları, performans sorunları, temiz kod prensipleri ve
  mimari kararlar üzerine yapılandırılmış geri bildirim sağlar.
---

# 🔍 Code Review Skill — Kod İnceleme Rehberi

## Amaç
Kodu güvenlik, performans, okunabilirlik ve sürdürülebilirlik açısından sistematik değerlendirmek.

## Talimatlar

### 1. Kodu Oku
- `read_file` ile incelenecek dosyayı oku.
- `diff_files` ile iki versiyon karşılaştırılıyorsa değişikliklere odaklan.
- Büyük dosyalarda önce genel yapıyı kavra, sonra detayları.

### 2. Güvenlik Kontrolü (Öncelikli)
- [ ] **SQL Injection**: Ham kullanıcı girdisi query'e giriyor mu?
- [ ] **Eval/exec kullanımı**: Kullanıcı girdisiyle çalıştırılıyor mu?
- [ ] **Path traversal**: Dosya yolları doğrulanıyor mu?
- [ ] **Kimlik doğrulama**: API endpoint'leri korumalı mı?
- [ ] **Hassas veri**: API key, parola düz metin olarak mı?
- [ ] **Input validation**: Kullanıcı girdisi doğrulanıyor mu?

### 3. Kod Kalitesi
- **Okunabilirlik**: İsimler anlamlı mı? Fonksiyonlar kısa mı?
- **DRY prensibi**: Kod tekrarı var mı?
- **SOLID**: Tek sorumluluk ihlali var mı?
- **Hata yönetimi**: try/except var mı, genel Exception yakalanıyor mu?
- **Yorum satırları**: Karmaşık mantık açıklanmış mı?

### 4. Performans
- N+1 sorgu problemi var mı?
- Gereksiz döngü içi işlem var mı?
- Büyük veri için bellek verimliliği düşünülmüş mü?
- Önbellek (cache) fırsatı var mı?

### 5. Geri Bildirim Formatı
Her bulgu için şu formatı kullan:

```
**[Önem: Kritik/Yüksek/Orta/Düşük]** — Kategori
Satır: <satır numarası veya fonksiyon adı>
Sorun: <kısa açıklama>
Neden önemli: <etki/risk>
Öneri: <düzeltme önerisi + kod örneği>
```

### 6. Özet
- Genel değerlendirme skoru (1-10)
- En kritik 3 bulgu
- Olumlu noktalar (motivasyon için önemli)

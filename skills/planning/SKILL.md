---
name: planning
description: >
  Karmaşık, çok adımlı görevleri alt görevlere bölme ve agent loop'unu
  verimli kullanma. Proje planlaması, önceliklendirme ve ilerleme takibi
  için yapılandırılmış yaklaşım.
---

# 🗺️ Planning Skill — Görev Planlama Rehberi

## Amaç
Büyük ve belirsiz görevleri somut, sıralı adımlara dönüştürmek
ve agent loop'unu en verimli şekilde kullanmak.

## Talimatlar

### 1. Görevi Anla ve Netleştir
Planlamadan önce şunları belirle:
- **Nihai hedef**: Başarı nasıl görünür? (somut çıktı)
- **Kısıtlar**: Zaman, kaynak, erişim sınırlamaları neler?
- **Bağımlılıklar**: Hangi adım hangisine bağlı?
- **Bilinmeyenler**: Araştırılması gereken şeyler var mı?

### 2. Görevi Parçala (WBS — Work Breakdown Structure)
```
Büyük Hedef
├── Faz 1: Araştırma ve Hazırlık
│   ├── Adım 1.1: Kaynak bul (web_search)
│   ├── Adım 1.2: Veri topla (web_fetch)
│   └── Adım 1.3: Bulguları kaydet (write_file)
├── Faz 2: Üretim
│   ├── Adım 2.1: ...
│   └── Adım 2.2: ...
└── Faz 3: Doğrulama
    └── Adım 3.1: ...
```

### 3. Önceliklendirme
Her adımı değerlendir:
- **Kritik yol**: Olmadan devam edilemeyen adımlar
- **Bağımlılık sırası**: Önce ne yapılmalı?
- **Hızlı kazanımlar**: Az çabayla yüksek değer verenler

### 4. Tool Seçimi
Her adım için doğru tool'u belirle:
| Görev Türü | Tool |
|-----------|------|
| Bilgi arama | `web_search`, `web_fetch` |
| Hesaplama | `calculator`, `run_python` |
| Veri işleme | `csv_query`, `data_summary` |
| Dosya üretimi | `write_file`, `append_file` |
| Kod geliştirme | `run_python`, `lint_code` |
| Görselleştirme | `chart_generate` |

### 5. İlerleme Takibi
- Her tamamlanan adımı rapor et: "✅ Adım X tamamlandı"
- Blocker varsa belirt ve alternatif yol öner
- Ara sonuçları `write_file` ile kaydet (güvenlik ağı)

### 6. Çıktı Belgele
Plan tamamlandığında:
- Ne yapıldığını özetle
- Üretilen dosyaları listele (workspace'dekiler)
- Sonraki adım önerisi sun

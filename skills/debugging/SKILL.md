---
name: debugging
description: >
  Hata mesajı analizi, stack trace okuma ve sistematik hata ayıklama stratejisi.
  Python, JavaScript ve genel programlama hatalarını tanımlamak ve çözmek için kullanılır.
---

# 🐛 Debugging Skill — Hata Ayıklama Stratejisi

## Amaç
Hataları hızlı, sistematik ve doğru şekilde tespit edip çözmek.

## Talimatlar

### 1. Hata Mesajını Oku ve Anla
- **Stack trace'i sondan başa oku** — asıl hata genellikle en altta.
- Hata türünü sınıflandır:
  - `SyntaxError` → Kod yazım hatası (indentation, parantez, virgül)
  - `NameError` / `AttributeError` → Tanımsız değişken/metod
  - `TypeError` → Yanlış tip (str yerine int vs.)
  - `ImportError` → Eksik paket veya yanlış import
  - `KeyError` / `IndexError` → Veri erişim hatası
  - `RuntimeError` → Çalışma zamanı mantık hatası
  - HTTP 4xx/5xx → API/ağ hatası

### 2. Olası Nedenleri Listele
- En muhtemelden en az muhtemele doğru sırala.
- Her neden için "bu neden olabilir mi?" sorusunu sor.
- Dış bağımlılıkları (kütüphaneler, API'ler, dosyalar) kontrol et.

### 3. İzolasyon ve Test
- `read_file` ile ilgili kodu oku.
- `run_python` ile küçük test parçaları çalıştır:
  ```python
  # Problematik satırı izole et
  print(type(değişken))
  print(değişken)
  ```
- Sorunu en küçük yeniden üretilebilir örneğe indir.

### 4. Düzeltme
- Düzeltilmiş kodu göster ve **ne değiştiğini açıkla**.
- Benzer hataların neden oluştuğunu anlat (eğitici).
- `write_file` ile düzeltilmiş versiyonu kaydet.

### 5. Doğrulama
- `run_python` ile düzeltilmiş kodu test et.
- Edge case'leri de test et (boş girdi, None, sınır değerleri).

### 6. Best Practices
- "Şansla çalışır" yaklaşımı yerine **neden çalıştığını** açıkla.
- Geçici yamalar yerine köklü çözümler öner.
- Loglama/hata yönetimi eksikse öneri olarak belirt.

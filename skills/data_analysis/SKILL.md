---
name: data_analysis
description: >
  CSV ve JSON veri setleri üzerinde analiz, istatistik ve görselleştirme.
  csv_query, data_summary ve chart_generate tool'larını kullanarak
  veri keşfi ve raporlama yapar.
---

# 📊 Data Analysis Skill — Veri Analizi Rehberi

## Amaç
Yapılandırılmış veri setlerini sistematik olarak keşfetmek, analiz etmek ve görselleştirmek.

## Talimatlar

### 1. Veri Keşfi (EDA — Exploratory Data Analysis)
Her analize şunlarla başla:

```
data_summary(path='veri.csv')
```
Kontrol et:
- Kaç satır/sütun var?
- Hangi sütunlar sayısal, hangileri kategorik?
- Değer aralıkları mantıklı mı (min/max)?
- Boş değer var mı?

### 2. Veri Okuma ve Filtreleme
```
csv_query(path='satis.csv', filter_col='şehir', filter_val='İstanbul')
csv_query(path='satis.csv', columns='tarih,gelir,müşteri', max_rows=20)
```

### 3. Temel Analiz Soruları
- **Dağılım**: Değerler nasıl dağılmış? Uç değerler (outlier) var mı?
- **Trend**: Zaman serisi varsa artış/azalış trendi var mı?
- **Karşılaştırma**: Gruplar arasında fark var mı?
- **Korelasyon**: İki değişken arasında ilişki var mı?

### 4. Görselleştirme
Bulguları grafikle destekle:

```
# Trend grafiği
chart_generate(
  data_json='{"x": [...tarihler...], "y": [...değerler...]}',
  chart_type='line',
  title='Aylık Satış Trendi',
  output_filename='trend.png'
)

# Karşılaştırma
chart_generate(
  data_json='{"x": ["Ocak","Şubat","Mart"], "y": [150, 180, 165]}',
  chart_type='bar',
  title='Aylık Karşılaştırma',
  output_filename='aylik.png'
)
```

### 5. Raporlama
Analiz sonucunda sun:
1. **Özet**: 3-5 cümleyle en önemli bulgular
2. **Metrikler**: Temel sayısal değerler (toplam, ortalama, en yüksek/düşük)
3. **Görsel**: İlgili grafik dosyası
4. **Öneri**: Verideki fırsat veya risk

### 6. Best Practices
- Küçük örnekle başla (max_rows=20), anlayınca büyük veriyi işle.
- Sayıları bağlama oturt: "180 satış" yerine "geçen aya göre %20 artış".
- Korelasyon ≠ nedensellik — bunu her zaman belirt.

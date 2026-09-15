---
name: prompt_engineering
description: >
  LLM'lerle etkili iletişim kurma, prompt tasarlama ve optimize etme.
  Daha doğru, tutarlı ve yapılandırılmış yanıtlar almak için
  prompt mühendisliği teknikleri ve best practice'ler.
---

# 🎯 Prompt Engineering Skill — Prompt Tasarım Rehberi

## Amaç
LLM'lerden maksimum fayda çıkarmak için etkili prompt tasarlamak.

## Talimatlar

### 1. Temel Prensipler
- **Açık ve spesifik ol**: "İyi bir e-posta yaz" yerine "B2B müşterisine ürün demo daveti e-postası yaz, ton profesyonel ama samimi olsun, 150 kelimeyi geçmesin."
- **Bağlam ver**: LLM ne bilmeli? Rol, konu, hedef kitle, format.
- **Format belirt**: "Madde madde listele", "Tablo formatında", "JSON olarak döndür".
- **Örnekler ver** (few-shot): İstediğin çıktının 1-2 örneğini göster.

### 2. Prompt Yapısı (Şablon)
```
Rol: [Kim olarak davranmalı]
Bağlam: [Arka plan bilgisi]
Görev: [Ne yapılacak — net eylem]
Format: [Çıktı formatı — liste/tablo/paragraf/JSON]
Kısıtlar: [Uzunluk, dil, ton, kaçınılacaklar]
Örnek: [İstenen çıktı örneği]
```

### 3. İleri Teknikler

**Chain of Thought (CoT):**
"Adım adım düşün ve çözümünü göster."

**Sistem Mesajı ile Rol Atama:**
```
Sistem: Sen deneyimli bir veri bilimci ve Python uzmanısın.
```

**Negatif Prompt (ne YAPMA):**
"Varsayım yapma, emin olmadığın bilgileri 'bilmiyorum' olarak belirt."

**Yapılandırılmış Çıktı İsteme:**
```
Yanıtını şu JSON formatında ver:
{
  "özet": "...",
  "bulgular": ["...", "..."],
  "sonraki_adım": "..."
}
```

### 4. Hata Giderme
- Yanıt çok genel mi? → Daha fazla bağlam ve kısıt ekle.
- Yanıt çok uzun mu? → "Maksimum X cümle/kelime" ekle.
- Format yanlış mı? → Örnek çıktı göster.
- Halüsinasyon mu? → "Yalnızca verilen bilgilere dayanarak yanıtla" ekle.

### 5. Astra Özelinde
Bu skill'i agent'ın kendi system prompt'unu iyileştirmek veya
kullanıcıya prompt yazma konusunda yardım etmek için kullan.

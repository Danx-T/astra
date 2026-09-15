---
name: sql_helper
description: >
  SQL sorgu yazma, optimizasyon ve veritabanı tasarım rehberi.
  SELECT, JOIN, aggregation, index kullanımı ve sık yapılan
  hatalar üzerine pratik talimatlar içerir.
---

# 🗄️ SQL Helper Skill — Veritabanı Sorgu Rehberi

## Amaç
Verimli, doğru ve güvenli SQL sorguları yazmak ve optimize etmek.

## Talimatlar

### 1. Sorgu Yazım Sırası
Her sorguyu şu sırayla düşün:
```sql
SELECT   -- 5. Hangi kolonlar?
FROM     -- 1. Hangi tablo?
JOIN     -- 2. Hangi tablolarla birleştir?
WHERE    -- 3. Hangi satırları filtrele?
GROUP BY -- 4. Nasıl grupla?
HAVING   -- 4b. Gruplanmış filtreleme
ORDER BY -- 6. Nasıl sırala?
LIMIT    -- 7. Kaç satır?
```

### 2. Yaygın Sorgular

**Temel SELECT:**
```sql
SELECT name, age, city
FROM users
WHERE age > 18
ORDER BY name ASC
LIMIT 100;
```

**JOIN türleri:**
```sql
-- INNER JOIN: her iki tabloda da olan
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN: sol tablo + eşleşenler (NULL dahil)
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

**Aggregation:**
```sql
SELECT
    city,
    COUNT(*) as toplam_musteri,
    AVG(age) as ort_yas,
    MAX(created_at) as son_kayit
FROM users
GROUP BY city
HAVING COUNT(*) > 10
ORDER BY toplam_musteri DESC;
```

### 3. Optimizasyon
- **INDEX**: Sık filtrelenen (`WHERE`) ve JOIN kolonlarına.
- **EXPLAIN**: `EXPLAIN SELECT ...` ile sorgu planını gör.
- **N+1 problemi**: Döngü içinde sorgu yerine tek JOIN.
- **SELECT \***: Yalnızca ihtiyaç duyulan kolonları seç.
- **LIMIT**: Büyük tablolarda test sorgularına ekle.

### 4. Güvenlik
- **SQL Injection**: Asla ham kullanıcı girdisi query'e girmesin.
  ```python
  # ✗ Kötü
  query = f"SELECT * FROM users WHERE name = '{user_input}'"

  # ✓ İyi (parametre binding)
  query = "SELECT * FROM users WHERE name = ?"
  cursor.execute(query, (user_input,))
  ```
- **Yetki**: Uygulama kullanıcısına sadece gerekli hakları ver.

### 5. SQLite Özellikleri (Astra'nın DB'si)
- Tip sistemi esnek: INTEGER, REAL, TEXT, BLOB, NULL
- `datetime('now')` — şu anki zaman
- `json_extract(col, '$.key')` — JSON kolon sorgulama
- PRAGMA: `PRAGMA table_info(users);` — tablo şeması

### 6. Sık Hatalar
- `GROUP BY` olmadan `COUNT()` → Hata
- `NULL` karşılaştırması: `= NULL` değil, `IS NULL`
- String'i tırnak içine almayı unutmak
- `HAVING` yerine `WHERE` kullanmak (aggregation filtresi için HAVING)

# Bilgi biriktirme örneği (referans)

> Bu dosya, sistemin bilgiyi **ders ders nasıl biriktirdiğini** gösteren bir örnektir. İçerik, test sırasında işlenen "Teknik Analiz Dersleri" serisinin **Ders 2** (`oQhdnKzsGyw`, Market Yapısı) ve **Ders 5** (`lsgS9gRoSgM`, Breaker & Mitigation) derslerinden alınmıştır. Gerçek wiki'ye buradan kopyalanmaz; her şey videolar işlendikçe yazılır.
>
> Örnek, Ders 5'in Ders 2'deki bir tanımı **inceltmesini** gösterir: aynı kural ID'si kalır, metni yeniden yazılır, değişiklik günlüğe ve kavram sayfasının "Tanımın Gelişimi" bölümüne tek satır olarak düşülür.

---

## 1. Playbook kuralları

### Ders 2 işlendikten sonra

```markdown
### MS-004: MSB / CHoCH (trend dönüşü)
- **Kural:** Trend BOĞA iken fiyat son **HL**'nin altına inerse → MSB, trend = AYI. Trend AYI iken son **LH**'nin üstüne çıkarsa → MSB, trend = BOĞA.
- **Parametreler:** kırılım_tipi = ? (bkz. Q-002)
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 11:19–14:29
- **Güven:** açık kural
- **Durum:** aktif
- **İlgili:** MS-005
```

### Ders 5 işlendikten sonra (çelişki → kullanıcı kararı: Ders 5 geçerli)

```markdown
### MS-004: MSB (trende ters yerel kırılım)
- **Kural:** Trend BOĞA iken fiyat son **HL**'nin altına inerse → MSB. Trend AYI iken son **LH**'nin üstüne çıkarsa → MSB. **MSB tek başına trendi çevirmez.** Trend ancak korunması gereken seviye kırılınca döner (→ CHoCH, MS-009).
- **Parametreler:** kırılım_tipi = ? (bkz. Q-002)
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 11:19–14:29 · [[Videos#lsgS9gRoSgM]] 3:21–4:16
- **Güven:** açık kural (Ders 5 tanımı; Ders 2'deki "MSB = CHoCH" ifadesi kullanıcı kararıyla geçersiz)
- **Durum:** aktif
- **İlgili:** MS-005, MS-008, MS-009, OB-001, OB-002

### MS-009: CHoCH (karakter değişimi = trend dönüşü)
- **Kural:** BOĞA iken fiyat **korunması gereken dibin** (MS-008) altına inerse → CHoCH, trend = AYI. AYI iken korunması gereken tepenin üstüne çıkarsa → CHoCH, trend = BOĞA.
- **Parametreler:** kırılım_tipi = ? (bkz. Q-002)
- **Kaynak:** [[Videos#lsgS9gRoSgM]] 3:21–4:16, 5:23–6:14
- **Güven:** açık kural
- **Durum:** aktif
- **İlgili:** MS-004, OB-001, OB-002
```

**Değişiklik yayılımı:** MS-004 değişince Claude, `İlgili` kurallarını (MS-005, SD-002 "BOS veya MSB" şartı…) ve "MSB" geçen tüm sayfaları (MarketStructure, TradingTerminology, kod taslakları) kontrol edip düzeltti.

**Kabul filtresi:** Eğitmenin "bunu canlı yayında söylediğimde bir günde ayı mı olur diye eleştirildim" anekdotu kural ID'si **almaz**; konu sayfasında not olarak kalır. "Korunması gereken dip kırılmadan trend dönmez" ise trend kararını değiştirdiği için kuraldır.

---

## 2. Açık sorular: `beklenen` durumu

```markdown
| ID | Soru | Durum | Açıldığı video | Cevaplandığı video | Cevap |
|----|------|-------|----------------|--------------------|-------|
| Q-002 | Kırılım için mum gövde kapanışı mı gerekir, fitil yeter mi? | açık | oQhdnKzsGyw | — | — |
| Q-020 | Breaker / mitigation block'un sınırları hangi mumlardan çizilir? | beklenen | lsgS9gRoSgM | — | Eğitmen: "Order Block dersinde anlatacağım" |
```

Order Block dersi işlenmeden önce Claude bu tabloyu okur ve Q-020'yi o derste özellikle arar (**ders öncesi aktif öğrenme**).

---

## 3. Kavram sayfası: "Tanımın Gelişimi" (MarketStructure.md sonu)

```markdown
## Tanımın Gelişimi
- Ders 5 ([[Videos#lsgS9gRoSgM]] 3:21): MSB ile CHoCH ayrıldı; MSB yerel kırılım, CHoCH korunması gereken seviyenin kırılması → karar: Ders 5 geçerli (MS-004, MS-009).
```

Sayfanın ana metni artık sadece güncel tanımı anlatır; eski "MSB = CHoCH" ifadesi metinde kalmaz.

---

## 4. Öğrenme günlüğü kaydı (LearningLog.md)

```markdown
## Ders 5: Breaker & Mitigation, MSB ve CHoCH farkı (lsgS9gRoSgM)
- **Tarih:** 2026-11-20 · **Transcript:** whisper (YouTube'dan doldurulan bölüm: 7)
- **Ders öncesi aranan:** Q-002 (kırılım tipi), Q-015 (temkinli girişte LTF)
- **Yeni öğrenilen:** MS-008, MS-009, MS-010, OB-001, OB-002, ENT-005 (açık kural) · yeni kavram: [[BreakerMitigationBlocks]]
- **İnceltilen / düzeltilen:** MS-004 (MSB artık trend dönüşü değil, yerel kırılım) · etkilenen sayfalar: [[MarketStructure]], [[TradingTerminology]]
- **Kapanan sorular:** Q-015 kısmen → örnek 4H → 15m (12:54)
- **Yeni sorular:** Q-020 (beklenen: Order Block dersi), Q-021, Q-022, Q-023
- **Çelişkiler:** Ders 2 "MSB = CHoCH" ↔ Ders 5 ayırıyor → karar: Ders 5 geçerli
- **Belirsiz kalan:** "tek hamlede kırılım" (ölçü yok)
- **Bilgi durumu:** aktif kural X (koda hazır Y) · açık soru Z · beklenen W · bekleyen çelişki V   ← playbook-check çıktısından
```

---

## 5. Bilgi Durumu panosu (Playbook.md başı, `playbook-check --write` üretir)

```markdown
| Kategori | Aktif | Koda hazır | Açık kural | Türetilmiş | Çelişkili | İptal |
|---|---|---|---|---|---|---|
| MS | 10 | 4 | 10 | 0 | 0 | 0 |
| OB | 2 | 0 | 2 | 0 | 0 | 0 |
| **Toplam** | **35** | **11** | 35 | 0 | 0 | 0 |

**Sorular:** 25 açık · 0 beklenen · 1 kısmen · 0 cevaplandı · **Bekleyen çelişki:** 0
```

"Koda hazır" = belirsiz (`?`) parametresi kalmamış ve çelişkisi olmayan aktif kural. Seri ilerledikçe bu sayının artması ve açık soru sayısının azalması beklenir.

# Playbook örneği (referans)

> Bu dosya, `docs/wiki/Playbook.md` dosyasına kuralların **nasıl** yazılacağını gösteren bir örnektir. İçerik, test sırasında işlenen "Teknik Analiz Dersleri — KONU 2: Market Yapısını Anlamak" (`oQhdnKzsGyw`) dersinden alınmıştır. Gerçek Playbook'a buradan kopyalanmaz; kurallar videolar işlendikçe Playbook'a yazılır.

## MS: Market Structure

### MS-001: Swing noktası etiketleme
- **Kural:** Yeni swing high > önceki swing high → **HH**, aksi halde **LH**. Yeni swing low > önceki swing low → **HL**, aksi halde **LL**.
- **Parametreler:** swing_tespit_yöntemi = ? (bkz. Q-001)
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 3:04–4:06, 11:19–12:23
- **Güven:** açık kural
- **Durum:** aktif
- **İlgili:** [[MarketStructure]], Q-001

### MS-002: Trend tanımı
- **Kural:** Son swing'ler HH + HL → trend = BOĞA. LH + LL → trend = AYI. Ne yeni HH ne yeni LL (fiyat iki seviye arasında) → trend = YATAY.
- **Parametreler:** —
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 3:04–6:07, 16:31
- **Güven:** açık kural
- **Durum:** aktif

### MS-003: BOS (trend yönünde kırılım)
- **Kural:** Trend BOĞA iken fiyat son swing high'ı kırarsa → BOS, trend devam. Trend AYI iken son swing low'u kırarsa → BOS.
- **Parametreler:** kırılım_tipi = ? (kapanış / fitil, bkz. Q-002)
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 4:06–5:07
- **Güven:** açık kural
- **Durum:** aktif

### MS-004: MSB / CHoCH (trend dönüşü)
- **Kural:** Trend BOĞA iken fiyat son **HL**'nin altına inerse → MSB, trend = AYI. Trend AYI iken son **LH**'nin üstüne çıkarsa → MSB, trend = BOĞA.
- **Parametreler:** kırılım_tipi = ? (bkz. Q-002)
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 11:19–14:29
- **Güven:** açık kural
- **Durum:** aktif
- **İlgili:** MS-005

### MS-005: AYI → BOĞA dönüşünde hangi tepe kırılmalı
- **Kural:** Trendi BOĞA'ya çevirmek için kırılması gereken seviye, **son LL'yi başlatan hareketin tepesidir**. Daha yakın küçük tepelerin kırılması MSB sayılmaz.
- **Parametreler:** —
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 29:51–30:51 (BTC günlük örneği)
- **Güven:** açık kural
- **Durum:** aktif

### MS-006: Zaman dilimine göre işlem yönü
- **Kural:** İşlem yönü = işlem alınan zaman diliminin trendi. HTF trendi ters yöndeyse işlem bir HTF düzeltmesi sayılır ve hedefler daraltılır.
- **Parametreler:** hedef_daraltma_oranı = ? (bkz. Q-004)
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 1:00–2:00, 35:54
- **Güven:** açık kural (daraltma oranı türetilmiş)
- **Durum:** aktif

### MS-007: Trend zayıflama bayrağı (tek başına sinyal değil)
- **Kural:** Ardışık HH'ler arası fark küçülüyorsa → "trend zayıflıyor" bayrağı. **Tek başına işlem sebebi değildir.**
- **Parametreler:** küçülme_eşiği = ? (bkz. Q-003)
- **Kaynak:** [[Videos#oQhdnKzsGyw]] 8:13–10:15
- **Güven:** açık kural (eşik yok)
- **Durum:** aktif

## Açık Sorular

| ID | Soru | Durum | Açıldığı video | Cevaplandığı video | Cevap |
|----|------|-------|----------------|--------------------|-------|
| Q-001 | Swing high/low nasıl tespit edilir (kaç mumluk pencere, fraktal mı)? | açık | oQhdnKzsGyw | — | — |
| Q-002 | Kırılım için mum gövde kapanışı mı gerekir, fitil yeter mi? | açık | oQhdnKzsGyw | — | — |
| Q-003 | "HH önceki tepeyi çok az geçti" için eşik ne? | açık | oQhdnKzsGyw | — | — |
| Q-004 | Karşı-trend (HTF'ye ters) işlemde hedef ne kadar daraltılır? | açık | oQhdnKzsGyw | — | — |
| Q-005 | Equal high/low için tolerans ne kadar (fitil sarkmaları kabul ediliyor)? | açık | oQhdnKzsGyw | — | — |

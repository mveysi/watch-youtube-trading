**Özet:** Videolardan öğrenilen tüm işlem kurallarının tek, kesin ve ölçülebilir listesi. Konu sayfaları (ör. [[MarketStructure]]) bir konuyu anlatır; Playbook ise **koda çevrilebilecek kuralları** ve henüz cevaplanmamış soruları tutar. İleride analiz/backtest sistemi sadece bu dosyayı okuyacak.
**Kütüphaneler/Teknolojiler:** Price Action, Market Structure, Smart Money Concepts, Supply & Demand
**Bağlantılar:** [[Index]], [[Videos]], [[TradingTerminology]]
**Kaynak Video:** Her kuralın kendi kaynağı aşağıda belirtilir.

---

## Nasıl kullanılır

- Her video işlendiğinde: yeni kurallar eklenir, mevcutlar güncellenir, cevaplanan sorular kapatılır, yeni sorular açılır, çelişkiler kaydedilir.
- **Kural kimlikleri:** `PA-` Price Action temel · `MS-` Market Structure · `SMC-` Smart Money · `SD-` Supply & Demand · `IMB-` Imbalance · `LIQ-` Likidite · `OB-` Order Block · `ENT-` Giriş · `RISK-` Risk/kasa yönetimi. Numara bir kez verildikten sonra değişmez; kural iptal edilirse silinmez, **Durum: iptal** yazılır.
- **Güven** alanı zorunlu:
  - `açık kural`: eğitmen bunu açıkça söyledi/gösterdi (dakikası belli)
  - `türetilmiş`: eğitmenin anlatımından çıkarıldı, kendisi böyle formüle etmedi
  - `çelişkili`: farklı kaynaklar farklı söylüyor → Çelişkiler tablosuna bak
- **Ölçülebilirlik standardı:** Kural, bir programcının tahmin yürütmeden koda çevirebileceği kadar net olmalı. Eğitmen bir sayı/eşik vermediyse **uydurulmaz**: parametre `?` bırakılır ve Açık Sorular'a eklenir.

| ❌ Kötü | ✅ İyi |
|--------|--------|
| "Güçlü kırılım aranır." | "Önceki swing high'ın üzerinde mum **gövde kapanışı**." |
| "Hacimli mumla uzaklaşmalı." | "Base'den çıkan mumun gövdesi ≥ X × son N mum ortalama gövdesi (X, N = ? → Q-0xx)" |
| "Bölgeye gelince girilir." | "Fiyat zone üst sınırına temas edince giriş; stop = zone alt sınırı − tampon (tampon = ? → Q-0xx)" |

Kural formatı:

```markdown
### MS-001: <kısa başlık>
- **Kural:** <koşul → sonuç, ölçülebilir>
- **Parametreler:** <ad = değer | ? (bkz. Q-0xx)>
- **Kaynak:** [[Videos#VIDEO_ID]] dk:sn–dk:sn
- **Güven:** açık kural | türetilmiş | çelişkili
- **Durum:** aktif | iptal (neden)
- **İlgili:** [[KonuSayfası]], Q-0xx, MS-00y
```

---

## Kurallar

<!-- Kurallar kategori başlıkları altında eklenir: ## PA, ## MS, ## SMC, ## SD, ## IMB, ## LIQ, ## OB, ## ENT, ## RISK -->

---

## Açık Sorular

| ID | Soru | Durum | Açıldığı video | Cevaplandığı video | Cevap |
|----|------|-------|----------------|--------------------|-------|

---

## Çelişkiler

İki kaynak aynı konuda farklı kural verirse ikisi de yazılır; hangisinin geçerli olduğu **kullanıcıya sorulur**, kendi başına seçilmez.

| Konu | Kaynak A (kural) | Kaynak B (kural) | Karar |
|------|------------------|------------------|-------|

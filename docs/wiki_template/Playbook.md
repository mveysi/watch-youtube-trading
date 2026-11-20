**Özet:** Videolardan öğrenilen tüm işlem kurallarının tek, kesin ve ölçülebilir listesi. Konu sayfaları (ör. MarketStructure) bir konuyu anlatır; Playbook ise **koda çevrilebilecek kuralları** ve henüz cevaplanmamış soruları tutar. İleride analiz/backtest sistemi sadece bu dosyayı okuyacak.
**Kütüphaneler/Teknolojiler:** Price Action, Market Structure, Smart Money Concepts, Supply & Demand
**Bağlantılar:** [[Index]], [[Videos]], [[LearningLog]]
**Kaynak Video:** Her kuralın kendi kaynağı aşağıda belirtilir.

<!-- BILGI-DURUMU:BASLA -->
## Bilgi Durumu

_Henüz ders işlenmedi. Bu blok `playbook-check --write` ile otomatik doldurulur, elle düzenlenmez._
<!-- BILGI-DURUMU:BITIR -->

---

## Nasıl kullanılır

- Her video işlendiğinde: yeni kurallar eklenir, mevcutlar güncellenir, cevaplanan sorular kapatılır, yeni sorular açılır, çelişkiler kaydedilir. Sonra `playbook-check --write` çalıştırılır (denetim + Bilgi Durumu).
- **Playbook'a ne girer (kabul filtresi):** bir programın **bir şeyi hesaplaması veya bir karar vermesi** için gereken her şey: tanımlar (swing, trend, bölge, imbalance nasıl tespit edilir), filtreler (haber saati, zaman dilimi uyumu), giriş/stop/hedef ve risk kuralları. **Girmez:** eğitmenin anekdotları, psikoloji, genel piyasa yorumları, motivasyon, "bence" tavsiyeleri; bunlar ilgili konu sayfasında not olarak kalır. Yeni kural açmadan önce mevcut bir kuralın inceltilmesi mi diye bak; öyleyse onu güncelle.
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

Durum değerleri: `açık` · `beklenen` (eğitmen "ilerideki derslerde anlatacağım" dedi; Cevap sütununa hangi konu/ders yazılır) · `kısmen cevaplandı` · `cevaplandı` · `iptal`. Yeni bir ders işlenmeden önce bu tablo okunur; ders bu soruları cevaplıyor mu diye bakılır.

| ID | Soru | Durum | Açıldığı video | Cevaplandığı video | Cevap |
|----|------|-------|----------------|--------------------|-------|

---

## Çelişkiler

İki kaynak aynı konuda farklı kural verirse ikisi de yazılır; hangisinin geçerli olduğu **kullanıcıya sorulur**, kendi başına seçilmez.

Ders serileri üst üste inşa edilir: ilk dersler kavramı basit anlatır, sonrakiler inceltir. Bu yüzden önerilen varsayılan, **aynı eğitmenin sonraki, konuya özel dersidir**. Karar verilince eski tanımı kullanan tüm konu sayfaları da düzeltilir.

*Karar* sütunu: karar beklenirken `⏳ Kullanıcı kararı bekleniyor. Öneri: …`; karar verilince `✅ <karar> (kullanıcı kararı, YYYY-AA-GG)` diye başlar.

| Konu | Kaynak A (kural) | Kaynak B (kural) | Karar |
|------|------------------|------------------|-------|

# Yol Haritası: Eğitim Fazı

> **Kime:** Bu repoyu kullanarak eğitim videolarını işleyecek kişiye (ve onun Claude Code'una).
> **Nasıl kullanılır:** Kurulumu [README.md](README.md)'ye göre yap, sonra Claude Code'a şunu yaz: *"YOL_HARITASI.md dosyasını oku ve seriyi 1. videodan işlemeye başla."*

## Amaç

Videolardan öğrenilen bilgiyi, ileride bir analiz/backtest sisteminin **doğrudan koda çevirebileceği** kadar net ve tutarlı hale getirmek. Backtest'te görülen "işlem kaçırma" sorunlarının önemli bir kısmı kuralların belirsiz kalmasından geliyor (ör. "kırılım için mum kapanışı mı gerekir, fitil yeter mi?"). Bu fazın hedefi bu belirsizlikleri sistematik olarak kapatmak.

## Sistem hazır: neler var? (2026-11-20)

| Parça | Ne yapıyor |
|------|-----------|
| **Görsel kare seçimi** | Ekran değişimi tabanlı, Türkçe/grafikli derslerde test edildi |
| **Whisper (Groq)** | Ses 10 dk'lık parçalara bölünür. Döngüye giren, boş kalan, Türkçe harfleri kesilen veya İngilizceye çevrilen bölümler otomatik olarak YouTube altyazısıyla doldurulur (`transcript.txt` içinde `[yt]` işaretli). |
| **Video indirme doğrulaması** | Yarım inen video dosyası tespit edilir ve başka yöntemle tekrar indirilir. Hiç kare çıkarılamazsa işlem hata vererek durur. |
| **Playbook** | `docs/wiki/Playbook.md`: tüm kuralların ID'li, kaynaklı ve ölçülebilir listesi + açık sorular + çelişkiler. Format: `docs/wiki_template/Playbook.md`, örnek: `docs/playbook_ornek.md` |
| **Kalite raporu** | Claude her videodan sonra kısa bir rapor verir (aşağıda) |

Bunların hepsi `CLAUDE.md` ve `.claude/skills/watch-youtube/SKILL.md` içinde tanımlı; Claude Code otomatik uygular.

---

## Görev: Seriyi sırayla işle

**Seri:** Teknik Analiz Dersleri — PRICE ACTION EĞİTİMİ
Playlist: `https://www.youtube.com/playlist?list=PLIKblNNaj9ePl_vLFa38zgu0cIdSiwOv4` (~24 konu, 30+ video)

**Adımlar (her video için):**
1. Claude Code'a videonun linkini yapıştır (playlist linki olabilir). Groq anahtarı tanımlıysa Claude otomatik olarak Whisper ile işler.
2. Claude: videoyu işler → wiki konu sayfalarını yazar → **Playbook'u günceller** → sonunda **Kalite Raporu** verir.
3. Sen raporu oku. Bir şey eksik/yanlış görünüyorsa Claude'a söyle. Raporda bir **çelişki** varsa karar senin: hangi kuralın geçerli olduğunu Claude'a bildir.
4. Sonraki videoya geç.

**Kurallar:**
- **Tek seri, sırayla.** Seri bitmeden başka eğitmenin videosu işlenmez (aynı kavrama farklı kurallar yazılmasın).
- Wiki boş başlar; ilk videoda Claude `docs/wiki/` klasörünü şablondan oluşturur.
- Altyazıda yeni bozuk terim çıkarsa Claude bunu `data/glossary_trading_tr.json` → `asr_corrections` içine ekler.
- `whisper_prompt` (aynı dosyada) **kısa, doğal bir cümle** olarak kalmalı (en fazla ~250 karakter). Uzun terim listesi Whisper'ı tamamen bozar. Seri yeni bir konuya geçerse (ör. order block) cümledeki terimler güncellenebilir.

**Ölçülebilir kural standardı:** Playbook'a yuvarlak ifade girmez.

| ❌ Kötü | ✅ İyi |
|--------|--------|
| "Güçlü kırılım aranır." | "Önceki swing high'ın üzerinde mum **gövde kapanışı**." |
| "Hacimli mumla uzaklaşmalı." | "Base'den çıkan mumun gövdesi ≥ X × son N mum ortalaması" (X, N bilinmiyorsa → açık soru) |
| "Fiyat bölgeye gelince girilir." | "Fiyat zone üst sınırına **temas ettiğinde** giriş; stop = zone alt sınırı − tampon" |

Eğitmen bir sayı vermediyse **uydurulmaz**: kural yazılır, eksik parametre açık soru olarak kaydedilir.

**Kalite Raporu örneği** (test sırasında bu serinin 5. dersi için üretilen gerçek rapor):

```
📋 Kalite Raporu: KONU 5 : BREAKER & MITIGATION KAVRAMLARI (MSB ve CHoCH FARKI)
- Transcript: whisper · YouTube'dan doldurulan bölüm: 7 · kaçmış görsel: yok
- Yeni kurallar: MS-008, MS-009, MS-010, OB-001, OB-002, ENT-005 (hepsi açık kural)
- Güncellenen kurallar: MS-004 → çelişkili
- Kapanan sorular: Q-015 kısmen (örnek 4H → 15m)
- Yeni açık sorular: Q-020 (blok sınırları), Q-021 ("tek hamle" tanımı), Q-022 (geçerli POI türleri), Q-023 (imbalance hedefi orta mı uç mu)
- Çelişkiler: 1 — Ders 2 "MSB = CHoCH" diyor, Ders 5 ikisini ayırıyor → kullanıcı kararı bekleniyor
- Hâlâ belirsiz ifadeler: "tek hamlede kırılım", blokların hangi mumlardan çizildiği (Order Block dersinde gelecek)
- Sözlüğe eklenen altyazı hataları: 4
```

Bu örnekteki gibi bir **çelişki** çıktığında karar senin. Aynı eğitmenin sonraki, konuya özel dersi genelde daha kesindir, ama Claude bunu kendi başına seçmez, sana sorar.

**Seri sonunda kontrol:**
- [ ] Serideki tüm videolar `docs/wiki/Videos.md` içinde kayıtlı.
- [ ] Playbook'taki açık soruların sayısı seri ilerledikçe azaldı; kalanlar listelenmiş.
- [ ] Çelişkiler tablosundaki her satırın "Karar" sütunu dolu.

---

## Sonraki faz (bu belgenin kapsamı dışında)

Eğitim fazı bitince Playbook'taki ölçülebilir kurallar, Binance OHLCV verisi üzerinde **Python ile hesaplanacak** (swing noktaları, BOS/MSB, imbalance, Fibonacci/OTE). Grafik ekran görüntüsünden "göz kararı" okuma yerine bu sayısal katman, backtest'teki işlem kaçırma sorununu çözmenin asıl yolu.

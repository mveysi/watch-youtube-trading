# Yol Haritası: Eğitim Fazı

> **Kime:** Bu repoyu kullanarak eğitim videolarını işleyecek kişiye (ve onun Claude Code'una).
> **Nasıl kullanılır:** Claude Code'a şunu yaz: *"YOL_HARITASI.md dosyasını oku, Görev 1'den başla."* Görevleri sırayla yap; her görevin sonundaki **kabul kriterleri** sağlanmadan sonrakine geçme.

## Amaç

Videolardan öğrenilen bilgiyi, ileride bir analiz/backtest sisteminin **doğrudan koda çevirebileceği** kadar net ve tutarlı hale getirmek. Backtest'te görülen "işlem kaçırma" sorunlarının önemli bir kısmı, kuralların belirsiz kalmasından kaynaklanıyor (ör. "kırılım için mum kapanışı mı gerekir, fitil yeter mi?"). Bu fazın hedefi bu belirsizlikleri sistematik olarak kapatmak.

## Mevcut durum (2026-11-20)

- Pipeline Türkçe ve grafikli derslerde test edildi (bkz. [DEGISIKLIKLER.md](DEGISIKLIKLER.md)).
- Test serisi: **Teknik Analiz Dersleri — PRICE ACTION EĞİTİMİ**
  Playlist: `https://www.youtube.com/playlist?list=PLIKblNNaj9ePl_vLFa38zgu0cIdSiwOv4` (~24 konu, 30+ video)
  İlk 4 ders test amaçlı işlendi; **senin wiki'n boş başlar, seriyi 1. videodan işle.**
- Bilinen sorun: Groq Whisper uzun seste **tekrar döngüsüne** giriyor ("BASE BASE BASE…") ve bazı bölümleri boş bırakıyor. 4. derste (`Lozc9tmDKOQ`) 5 döngü ve 2 boş bölüm oluştu. → Görev 1

---

## Görev 1: Whisper'ı güvenilir hale getir (kod)

**Neden:** Tüm seri `--whisper -l tr` ile işlenecek. Whisper terimleri YouTube altyazısından çok daha doğru yazıyor ("Smart Money" 10'a 0, "Demand" 14'e 0), ama döngü ve boşluklar elle düzeltilmek zorunda kalıyor.

**Yapılacaklar** (`watch_youtube/downloader.py`):
1. **Parçalara böl:** Sesi ffmpeg ile ~10 dakikalık parçalara ayır (parçalar arası ~5 sn örtüşme). Her parçayı ayrı ayrı Whisper'a gönder, zaman damgalarını parçanın başlangıç saniyesi kadar kaydırarak birleştir, örtüşen kısımdaki tekrarları at.
2. **Bozuk bölümleri tespit et:** Bir Whisper segmenti şu durumlarda "bozuk" sayılsın:
   - aynı kelime veya 2–3 kelimelik grup art arda 4+ kez tekrar ediyorsa ("BASE BASE BASE", "Arz Bölgesi Arz Bölgesi…"),
   - ya da metin aşırı kısaysa ve 30+ saniyelik bir aralıkta neredeyse hiç metin yoksa (boşluk).
3. **Otomatik doldur:** Bozuk segmentlerin ve boşlukların zaman aralığını YouTube altyazısından (`transcript_raw.vtt`) gelen satırlarla değiştir.
4. `transcript.txt` içinde YouTube'dan doldurulan paragrafları işaretle (ör. satır başına `[yt]`), ki wiki yazılırken o kısımlardaki terimlerin daha az güvenilir olduğu bilinsin.
5. `metadata.json` dosyasına kaç segmentin düzeltildiğini yaz (`whisper_repaired_segments`).

**Kabul kriterleri:**
- [ ] `watch-youtube "https://www.youtube.com/watch?v=Lozc9tmDKOQ" -o ./output --whisper -l tr` sonrası `transcript.txt` içinde aynı kelimenin art arda 4+ kez tekrarı yok.
- [ ] Bu videoda 20:32 ve 29:05 civarındaki bölümler boş değil.
- [ ] "Smart Money", "Demand", "Supply" terimleri hâlâ Whisper'dan doğru geliyor.
- [ ] Groq anahtarı yokken pipeline eskisi gibi YouTube altyazısıyla çalışıyor.

---

## Görev 2: Playbook (tek kural kitabı) kur (wiki + skill talimatı)

**Neden:** Kurallar ve açık sorular şu an konu sayfalarına dağılıyor. 15+ video sonra hangi sorunun cevaplandığını takip etmek imkânsızlaşır ve farklı videolardaki çelişkiler fark edilmez. İleride bot tarafı **sadece bu dosyayı** okuyacak.

**Yapılacaklar:**

1. `docs/wiki/Playbook.md` dosyasını oluştur. Her kural şu formatta:

   ```markdown
   ### MS-003: Boğa trendinde MSB (trend dönüşü)
   - **Kural:** Trend BOĞA iken fiyat son Higher Low'un altına inerse → MSB, trend = AYI.
   - **Parametreler:** kırılım_tipi = ? (kapanış / fitil — bkz. Q-002)
   - **Kaynak:** [[Videos#oQhdnKzsGyw]] 12:23–13:27 · eğitmenin açık kuralı
   - **Güven:** açık kural | türetilmiş | çelişkili
   - **İlgili:** [[MarketStructure]], Q-002
   ```

   - Kural kimlikleri kategoriye göre: `PA-` (Price Action temel), `MS-` (Market Structure), `SMC-` (Smart Money), `SD-` (Supply & Demand), `IMB-` (Imbalance), `RISK-`…
   - **"Güven"** alanı zorunlu: eğitmenin açıkça söylediği kural mı, Claude'un çıkarımı mı?

2. Aynı dosyada **Açık Sorular** tablosu:

   | ID | Soru | Durum | Açıldığı video | Cevaplandığı video | Cevap |
   |----|------|-------|----------------|--------------------|-------|
   | Q-002 | Kırılım için mum kapanışı mı gerekir, fitil yeter mi? | açık | oQhdnKzsGyw | — | — |

3. **Çelişkiler** bölümü: iki video aynı konuda farklı kural verirse ikisi de yazılır, hangisinin geçerli olduğu kullanıcıya sorulur. Kendi başına seçim yapılmaz.

4. `.claude/skills/watch-youtube/SKILL.md` dosyasına şu adımları ekle (her video işlendiğinde):
   - Yeni kuralları Playbook'a ekle, mevcutları güncelle.
   - Bu videonun cevapladığı açık soruları kapat (durum + video + cevap).
   - Yeni açık soruları ekle.
   - Video sonunda kullanıcıya **Kalite Raporu** ver (şablon aşağıda).

**Kabul kriterleri:**
- [ ] İlk işlenen videodan itibaren Playbook dolmaya başlıyor; her kuralın kaynak video + dakikası var.
- [ ] Açık soruların hepsi tek tabloda, ID'li.
- [ ] Konu sayfalarındaki "Bot / Uygulama İçin Çıkarılabilir Kurallar" bölümleri Playbook'taki ID'lere bağlantı veriyor.

---

## Görev 3: Seriyi sırayla işle (eğitim fazı)

**Kurallar:**
- **Tek seri, sırayla.** Seri bitmeden başka eğitmenin videosu işlenmez (aynı kavrama farklı kurallar yazılmasın).
- Her video `--whisper -l tr` ile işlenir (Claude Code'a "Whisper ile işle" demek yeterli).
- Altyazıda yeni bozuk terim çıkarsa `data/glossary_trading_tr.json` → `asr_corrections` içine eklenir. Yeni bir trading terimi sık geçiyorsa `whisper_prompt` içine de eklenir.

**Ölçülebilir kural standardı.** Playbook'a ve "Bot için kurallar" bölümlerine yuvarlak ifade girmez:

| ❌ Kötü | ✅ İyi |
|--------|--------|
| "Güçlü kırılım aranır." | "Önceki swing high'ın üzerinde mum **gövde kapanışı**." |
| "Hacimli mumla uzaklaşmalı." | "Base'den çıkan ilk mumun gövdesi son 20 mum ortalama gövdesinin ≥ X katı" (X bilinmiyorsa → açık soru) |
| "Fiyat bölgeye gelince girilir." | "Fiyat zone'un üst sınırına **temas ettiğinde** limit giriş; stop = zone alt sınırı − tampon" |

Eğitmen bir sayı vermediyse **uydurma**: kuralı yaz, eksik parametreyi açık soru olarak kaydet.

**Her video sonunda Claude'un vereceği Kalite Raporu:**

```
📋 Kalite Raporu: <video başlığı>
- Yeni kurallar: SD-004, SD-005 (açık kural), IMB-002 (türetilmiş)
- Güncellenen kurallar: MS-003 (kırılım tipi netleşti)
- Kapanan sorular: Q-002 → "gövde kapanışı gerekir" (12:40)
- Yeni açık sorular: Q-011 (base en az kaç mum?)
- Hâlâ belirsiz ifadeler: "hacimli mum" (ölçü yok)
- Sözlüğe eklenen altyazı hataları: 3
- Kaçmış olabilecek görseller: yok / <dakika + açıklama>
```

Senin işin her videodan sonra bu raporu okumak. Bir şey yanlış veya eksik görünüyorsa Claude'a söyle.

**Kabul kriterleri (seri sonunda):**
- [ ] Serideki tüm videolar `Videos.md` içinde kayıtlı.
- [ ] Playbook'taki açık soruların sayısı seri ilerledikçe azalıyor; kalanlar seri sonunda listelenmiş.
- [ ] Çelişkiler bölümü kullanıcıyla birlikte çözülmüş.

---

## Sonraki faz (bu belgenin kapsamı dışında)

Eğitim fazı bitince Playbook'taki ölçülebilir kurallar, Binance OHLCV verisi üzerinde **Python ile hesaplanacak**: swing noktaları, BOS/MSB, imbalance, Fibonacci/OTE. Grafik ekran görüntüsünden "göz kararı" okuma yerine bu sayısal katman, backtest'teki işlem kaçırma sorununu çözmenin asıl yolu.

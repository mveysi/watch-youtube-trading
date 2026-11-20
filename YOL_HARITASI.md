# Yol Haritası: Aşama 1 ve Aşama 2

> **Kime:** Bu repoyu kendi bilgisayarında Claude Code ile ilerletecek kişiye (ve onun Claude'una).
> **Ne anlatır:** Kurulumdan başlayarak iki aşamayı hangi sırayla, nasıl ilerleteceğini; nerede durup proje sahibine danışacağını; ona ne göndereceğini.

## Büyük resim

| | Aşama 1: Öğrenme | Aşama 2: Analiz motoru |
|---|---|---|
| **Ne** | YouTube derslerini işleyip işlem kurallarını `docs/wiki/Playbook.md` içinde biriktirmek | Playbook'taki kuralları kripto mum verisi üzerinde Python ile hesaplayan motoru yazmak |
| **Nerede** | Repo kökü, `main` dalı | `asama2_kripto_analiz/` klasörü, `asama-2` dalı |
| **Ne zaman** | Hemen, 1. dersten | Aşama 1'de en az **1–6. dersler** işlendikten sonra (motorun ilk kuralları bu derslerden gelir), Aşama 1 ile **paralel** devam eder |
| **GitHub'a gider mi** | Hayır. Wiki senin bilgisayarında kalır. | Evet, `asama-2` dalına. `main`'e sadece proje sahibi alır. |

**Altın kurallar:**
- Aşama 1'de **sıra önemli:** dersleri playlist sırasıyla işle, seri bitmeden başka eğitmenin videosunu ekleme.
- Aşama 2'de **ANAYASA üstündür:** [asama2_kripto_analiz/ANAYASA.md](asama2_kripto_analiz/ANAYASA.md) değişmez; gerçek emir yok, Aşama 1'e dokunmak yok.
- **Karar senin değil, proje sahibinin olan yerler** aşağıda 🛑 ile işaretli. Oralarda dur, ona danış.

---

## 0. Kurulum (bir kez)

1. [README.md](README.md) bölüm 3'e göre kur: Python, `.venv`, `pip install -r requirements.txt`, `pip install -e .`, ffmpeg (`winget install Gyan.FFmpeg` veya zip'i `tools/` altına çıkar, otomatik bulunur).
2. Groq anahtarını ortam değişkeni olarak tanımla (README bölüm 5). Anahtarı **hiçbir dosyaya, sohbete veya repoya yazma**.
3. Proje klasörünü VS Code'da aç, Claude Code'u başlat. "Bu klasöre güveniyor musun?" (trust) sorusunu **onayla**. Bu, devam notlarını compact'tan sonra otomatik okutan hook'un çalışması için gerekli.
4. Repo sonradan güncellenirse (`git pull`), bir kez `pip install -e .` çalıştır (`playbook-check` komutu böyle kurulur).

---

## 1. Aşama 1: Seriyi işle (öğrenme)

**Seri:** Teknik Analiz Dersleri — PRICE ACTION EĞİTİMİ
Playlist: `https://www.youtube.com/playlist?list=PLIKblNNaj9ePl_vLFa38zgu0cIdSiwOv4` (~24 konu, 30+ video)

**Başlatmak için** Claude Code'a yaz: *"YOL_HARITASI.md dosyasını oku ve seriyi 1. videodan işlemeye başla."*

### Her ders için döngü

1. Dersin linkini Claude Code'a yapıştır (playlist linki olabilir).
2. Claude kendisi şunları yapar: videoyu işler (Whisper ile) → açık soruları okuyup dersi onlara bakarak izler → kavram sayfalarını ve **Playbook'u** günceller → değişiklikleri bağlı sayfalara yayar → `playbook-check` ile denetler → `LearningLog.md` ve `DEVAM.md` notlarını günceller → sonunda **Kalite Raporu** verir.
3. Raporu oku. Eksik/yanlış görünen bir şey varsa Claude'a söyle.
4. 🛑 Raporda **çelişki** varsa (iki ders aynı konuda farklı kural veriyor): Claude bir öneri sunar (genelde sonraki, konuya özel ders). Kararı ver; emin değilsen proje sahibine sor.
5. Sonraki derse geç.

### Proje sahibine gönder

- **İlk 2 dersin** Kalite Raporunu ve `docs/wiki/LearningLog.md` dosyasındaki kayıtlarını gönder. Sistemin yeni öğrenme akışı ilk kez sende tam çalışacak; bir aksaklık varsa seri başında düzeltilir.
- Sonrasında her **5 derste bir** Kalite Raporlarını ve Playbook'un en üstündeki **Bilgi Durumu** panosunu gönder (kaç kural, kaçı koda hazır, kaç soru açık).
- Bir derste hata/garip bir durum olursa hemen.

### Bilmen gerekenler

- Wiki boş başlar; ilk derste Claude `docs/wiki/` klasörünü şablondan oluşturur. `docs/wiki/` GitHub'a gitmez.
- Bilgi durumunu kendin görmek için: `.venv\Scripts\playbook-check.exe`.
- Altyazıda yeni bozuk terim çıkarsa Claude bunu `data/glossary_trading_tr.json` → `asr_corrections` içine ekler. Aynı dosyadaki `whisper_prompt` **kısa, doğal bir cümle** kalmalı (en fazla ~250 karakter); uzun terim listesi Whisper'ı bozar.
- **Ölçülebilir kural standardı:** Playbook'a yuvarlak ifade girmez. Eğitmen sayı vermediyse uydurulmaz; kural yazılır, eksik kısım açık soru olur.

| ❌ Kötü | ✅ İyi |
|--------|--------|
| "Güçlü kırılım aranır." | "Önceki swing high'ın üzerinde mum **gövde kapanışı**." |
| "Hacimli mumla uzaklaşmalı." | "Base'den çıkan mumun gövdesi ≥ X × son N mum ortalaması" (X, N bilinmiyorsa → açık soru) |
| "Fiyat bölgeye gelince girilir." | "Fiyat zone üst sınırına **temas ettiğinde** giriş; stop = zone alt sınırı − tampon" |

**Kalite Raporu örneği** (test sırasında bu serinin 5. dersi için üretilen gerçek rapor):

```
📋 Kalite Raporu: KONU 5 : BREAKER & MITIGATION KAVRAMLARI (MSB ve CHoCH FARKI)
- Transcript: whisper · YouTube'dan doldurulan bölüm: 7 · kaçmış görsel: yok
- Ders öncesi aranan sorular: Q-002, Q-015 → cevaplanan: Q-015 kısmen · cevapsız kalan: Q-002
- Yeni kurallar: MS-008, MS-009, MS-010, OB-001, OB-002, ENT-005 (hepsi açık kural)
- Güncellenen kurallar: MS-004 → çelişkili
- Kapanan sorular: Q-015 kısmen (örnek 4H → 15m)
- Yeni açık sorular: Q-020 (blok sınırları), Q-021 ("tek hamle" tanımı), Q-022 (geçerli POI türleri), Q-023 (imbalance hedefi orta mı uç mu)
- Çelişkiler: 1 — Ders 2 "MSB = CHoCH" diyor, Ders 5 ikisini ayırıyor → kullanıcı kararı bekleniyor
- Hâlâ belirsiz ifadeler: "tek hamlede kırılım", blokların hangi mumlardan çizildiği (Order Block dersinde gelecek)
- Sözlüğe eklenen altyazı hataları: 4
```

Bu çelişkide proje sahibinin kararı: **Ders 5 geçerli** (MSB = trende ters yerel kırılım, CHoCH = korunması gereken seviyenin kırılması = trend dönüşü). Seriyi baştan işlerken aynı çelişki 5. derste tekrar çıkacak; aynı kararı verebilirsin.

Tamamlanmış örnek (kural inceltme, `beklenen` soru, günlük kaydı, pano): [docs/playbook_ornek.md](docs/playbook_ornek.md).

### Seri sonunda kontrol

- [ ] Serideki tüm videolar `docs/wiki/Videos.md` içinde kayıtlı.
- [ ] Açık soru sayısı seri boyunca azaldı; `beklenen` durumunda soru kalmadı.
- [ ] `playbook-check` hatasız; `LearningLog.md`'de her video için kayıt var.
- [ ] Çelişkiler tablosundaki her satırın "Karar" sütunu dolu (✅ ile başlıyor).

---

## 2. Aşama 2: Analiz motorunu yaz

**Ne zaman başla:** Aşama 1'de **en az 1–6. dersler** işlendiğinde (market yapısı 2. ve 5. derste, imbalance 4. derste öğretiliyor; Adım 0 için 2. dersin storyboard kareleri `output/oQhdnKzsGyw/` altında olmalı). Aşama 1'e paralel devam edersin: bir gün ders, bir gün motor gibi.

### Başlangıç (bir kez)

```bash
git pull
git checkout -b asama-2
cp asama2_kripto_analiz/kurulum/settings.local.json.ornek .claude/settings.local.json
```

Üçüncü satır korumayı açar: Claude ANAYASA'yı, koruma düzeneğini, Aşama 1 kodunu düzenleyemez ve `main`'e push edemez. (Zaten bir `.claude/settings.local.json` varsa üzerine yazma; `deny` listesini ekle.)

Sonra Claude Code'a yaz: *"asama2_kripto_analiz/PLAN.md ve asama2_kripto_analiz/CLAUDE.md dosyalarını oku, Adım 0'dan başla."*

### Adım adım akış

| Adım | Claude ne yapar | Sen ne yaparsın |
|---|---|---|
| **0. Doğru cevapları dondur** | `beklenen/btc_1d_2021_2022.md` içindeki aday noktaları storyboard ve gerçek veriyle doğrular | 🛑 Listeyi eğitmenin grafiğiyle karşılaştır, **proje sahibiyle birlikte onayla**. Onaylanınca dosya push edilir ve **proje sahibi `main`'e alır** (dondurma, aşağıda). |
| **1. Veri** | Binance'ten mum verisi çeker (yedek: Yahoo/CSV) | Kabul kriterindeki fiyatları kontrol et |
| **2. Ayarlar** | Açık soruları ayar dosyasına çevirir | — |
| **3. Market yapısı** | Swing, HH/HL, BOS/MSB/CHoCH, testler | Testlerin geçtiğini gör |
| **4. Imbalance** | 3 mum kuralı + testler | — |
| **5. Grafik** | Etiketli grafik resmi | Resmi açıp okuyabildiğini kontrol et |
| **6. Kabul testi** | BTC 2021–2022'de motoru çalıştırır, ayar kalibrasyonu, rapor | 🛑 Grafiği eğitmenin ekran görüntüsüyle **yan yana** incele; raporu ve grafiği proje sahibine gönder |
| **7. Teslim** | README, son push | Proje sahibine "bitti" de |

Her adımın sonunda Claude kanıtıyla (test çıktısı, grafik dosyası) kısa rapor verir, `DEVAM.md`'yi günceller ve push etmeden önce koruma kontrolünü çalıştırır.

### Dondurma (Adım 0 sonunda, bir kez)

Dondurma = onaylanmış doğru cevaplar dosyasının `main`'e alınması. Sonrasında o dosya `asama-2`'de değişirse GitHub kırmızı verir.

1. Claude dosyanın durum satırını `> **Durum: ONAYLANDI (YYYY-AA-GG)**` yapar, commit'ler, `asama-2`'ye push eder.
2. 🛑 Proje sahibine haber ver. O (kendi Claude'una "beklenen dosyasını main'e al" diyerek) dosyayı `main`'e alır.
3. Sen dalını güncelle: `git fetch` ve `git merge origin/main`.

### Plan tutmazsa

Plan bir tahmindir; Claude onu güncelleyebilir ([PLAN.md](asama2_kripto_analiz/PLAN.md) §8): yöntem değişikliği serbest (sana bildirir), kapsam veya kabul kriteri değişikliği **senin onayınla**, ANAYASA'daki her şey yasak. Her değişiklik PLAN.md'deki **Plan Değişiklik Günlüğü**'ne yazılır. 🛑 Kabul kriterinin gevşetilmesi önerilirse proje sahibine sor.

### Proje sahibine gönder

- Adım 0 sonunda: onaylanacak liste.
- Adım 6 sonunda: `ciktilar/kabul_raporu.md` ve grafik resmi.
- Bir yöntem iki kez tutmayıp Claude sana sorduğunda: Claude'un yazdığı özet.
- GitHub'da `asama2-koruma` kontrolü kırmızı verirse: hemen (Claude korunan bir şeye dokunmuş demektir).

---

## 3. Git dalları: hangi iş nerede

| İş | Dal | Not |
|---|---|---|
| Ders işleme (Aşama 1) | `main` | Wiki (`docs/wiki/`) ve `output/` git'e girmez, dal değiştirince kaybolmaz |
| Analiz motoru (Aşama 2) | `asama-2` | Sadece `asama2_kripto_analiz/` içinde değişiklik |
| Dal değiştirmek | `git checkout main` / `git checkout asama-2` | Önce yarım iş varsa commit'le |
| Repo güncellemesi almak | `main`'de `git pull`; sonra `asama-2`'de `git merge main` | |

Aşama 1'de GitHub'a bir şey göndermen gerekmez. Sözlük (`data/glossary_trading_tr.json`) güncellemelerini paylaşmak istersen proje sahibine söyle.

---

## 4. Compact ve uzun çalışma

- Claude her ders/adım sonunda devam notunu günceller: Aşama 1 → `docs/wiki/DEVAM.md`, Aşama 2 → `asama2_kripto_analiz/DEVAM.md`.
- Claude Code her açıldığında, compact'tan ve kaldığı yerden devam ettiğinde bu notlar Claude'a **otomatik** okutulur.
- Compact'tan sonra Claude kaldığı yeri doğru söylemiyorsa: *"DEVAM.md dosyalarını oku ve nerede kaldığımızı özetle"* de.
- İstersen compact'a talimat ver: `/compact bekleyen kararları ve son işlenen dersi koru`.

---

## 5. Sorun giderme

| Sorun | Çözüm |
|---|---|
| YouTube: "Sign in to confirm you're not a bot" | Çok indirme sonrası geçici engel. Birkaç saat bekle **veya** Chrome'a "Get cookies.txt LOCALLY" eklentisini kur, youtube.com'da giriş yapmışken Export de, dosyayı `cookies.txt` adıyla proje köküne koy (otomatik kullanılır). Bu dosyayı **kimseyle paylaşma**. |
| `playbook-check` bulunamadı | `pip install -e .` |
| `playbook-check` ✖ hata veriyor | Claude'a "playbook-check hatalarını düzelt" de |
| Binance verisine bağlanamıyor | Bazı ağlarda kripto siteleri engelli. Claude PLAN.md'deki yedek kaynaklara geçer (Binance arşivi → Yahoo → CSV). |
| GitHub'da `asama2-koruma` kırmızı | Claude korunan bir dosyaya dokunmuş. Değişikliği geri aldır, proje sahibine bildir. |
| Claude bir şeyi "izin verilmedi" diye yapamıyor | Koruma ayarı çalışıyor demektir. Gerçekten gerekliyse proje sahibine sor; ayarı kendin gevşetme. |
| Diğer sorunlar | README.md bölüm 12 |

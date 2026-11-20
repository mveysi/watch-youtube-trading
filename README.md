# watch-youtube: YouTube videolarından öğrenen bilgi bankası

YouTube'daki eğitim videolarını **Claude'a "izletip"** öğrendiklerini düzenli notlar halinde saklayan bir araç.

Bir video linki verirsin. Araç videoyu indirir, **konuşulanları yazıya döker**, **ekranda gösterilen önemli anların (slayt, grafik, çizim) görüntülerini** toplar. Claude bunların hepsini inceleyip öğrendiklerini `docs/wiki/` klasörüne konu konu yazar. Sonra "BOS nedir?", "arz bölgesi nasıl çizilir?" gibi sorular sorduğunda Claude cevabı bu notlardan, hangi videodan öğrendiğini belirterek verir.

> **Kimin için?** Bir konuyu (ör. borsa / Price Action eğitimi) YouTube videolarından öğrenip bu bilgiyi kalıcı, aranabilir ve ileride başka sistemlerde (ör. bir analiz botunda) kullanılabilir halde tutmak isteyenler için.

---

## İçindekiler

1. [Nasıl çalışır?](#1-nasıl-çalışır)
2. [Gerekenler](#2-gerekenler)
3. [Kurulum: Windows](#3-kurulum-windows)
4. [Kurulum: macOS / Linux](#4-kurulum-macos--linux)
5. [İsteğe bağlı: Groq API anahtarı (Türkçe videolar için önerilir)](#5-isteğe-bağlı-groq-api-anahtarı)
6. [Kullanım 1: Claude Code ile (asıl kullanım)](#6-kullanım-1-claude-code-ile-asıl-kullanım)
7. [Kullanım 2: Sadece komut satırı](#7-kullanım-2-sadece-komut-satırı)
8. [Çıktılar: Hangi dosya ne işe yarar?](#8-çıktılar)
9. [Tüm seçenekler](#9-tüm-seçenekler)
10. [Proje yapısı](#10-proje-yapısı)
11. [Teknik detaylar](#11-teknik-detaylar)
12. [Sorun giderme](#12-sorun-giderme)
13. [Bilinen sınırlamalar](#13-bilinen-sınırlamalar)
14. [Teşekkür](#14-teşekkür)

---

## 1. Nasıl çalışır?

```
YouTube linki
     │
     ▼
① İndirme ────────── Altyazı (YouTube) veya Groq Whisper ile yazıya dökme + video dosyası
     │
     ▼
② Kare seçimi ────── Ekranın değiştiği anlar tespit edilir (yeni slayt, çizim, grafik);
     │                her sahnenin "son hali" alınır. Dilden bağımsız çalışır.
     ▼
③ Storyboard ─────── Seçilen kareler 3×3 ızgaralara dizilir, altına o an konuşulan metin yazılır
     │
     ▼
④ Analiz (Claude) ── Claude storyboard görsellerini + tam transcript'i okur
     │
     ▼
⑤ Wiki ──────────── Öğrenilenler docs/wiki/ altına Obsidian formatında konu sayfaları olarak yazılır
```

**Neden sadece altyazı yetmiyor?** Eğitim videolarında bilginin büyük kısmı ekranda gösterilir (grafik üzerindeki etiketler, slayttaki tanımlar, çizimler). Bu yüzden araç hem *ne söylendiğini* hem *ne gösterildiğini* toplar. Tüm videoyu göndermek yerine sadece anlamlı kareleri ızgaralara sıkıştırdığı için Claude'un okuması gereken görsel miktarı da (ve maliyeti) çok azalır.

①–③ adımlarını Python aracı (`watch-youtube` komutu) yapar. ④–⑤ adımlarını Claude Code yapar.

---

## 2. Gerekenler

| Gereken | Neden | Not |
|--------|-------|-----|
| **Python 3.11 veya üstü** | Aracın kendisi | [python.org/downloads](https://www.python.org/downloads/). Windows'ta kurarken **"Add Python to PATH"** kutusunu işaretle. |
| **Git** | Repoyu indirmek için | [git-scm.com](https://git-scm.com/) |
| **ffmpeg** | Videodan kare almak için | Kurulumu aşağıda |
| **Claude Code** | Videoyu analiz edip wiki yazmak için | [claude.com/claude-code](https://claude.com/claude-code). VS Code eklentisi veya terminal sürümü. Sadece komut satırını kullanacaksan şart değil. |
| Groq API anahtarı | *İsteğe bağlı.* Daha iyi yazıya dökme | Ücretsiz, bkz. [bölüm 5](#5-isteğe-bağlı-groq-api-anahtarı) |

---

## 3. Kurulum: Windows

Tüm komutları **PowerShell**'de çalıştır (Başlat menüsü → "PowerShell" yaz). VS Code kullanıyorsan **Terminal → New Terminal** da olur.

**1) Repoyu indir**

```powershell
git clone https://github.com/mveysi/watch-youtube-trading.git
cd watch-youtube-trading
```

**2) Sanal ortam oluştur ve etkinleştir**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> Satırın başında `(.venv)` görmelisin. "running scripts is disabled" hatası alırsan önce bunu çalıştırıp tekrar dene:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

**3) Python paketlerini kur**

```powershell
pip install -r requirements.txt
pip install -e .
python -m spacy download en_core_web_sm
```

**4) ffmpeg'i kur**

```powershell
winget install Gyan.FFmpeg
```

Kurulumdan sonra **terminali kapatıp yeniden aç** ve kontrol et:

```powershell
ffmpeg -version
```

> `winget` yoksa: [ffmpeg.org/download.html](https://ffmpeg.org/download.html) adresinden Windows "essentials" paketini indir ve zip'i proje içinde `tools/` klasörüne çıkar (sonuç: `tools/ffmpeg-<sürüm>-essentials_build/bin/ffmpeg.exe`). Bu klasör GitHub'a yüklenmez.

**5) Türkçe karakter ayarı** (konsolda `UnicodeEncodeError` almamak için)

```powershell
setx PYTHONIOENCODING utf-8
```

Sonra terminali kapatıp aç.

**6) Test et**

```powershell
.venv\Scripts\Activate.ps1
watch-youtube --help
```

Seçenek listesi görünüyorsa kurulum tamam. ✅

---

## 4. Kurulum: macOS / Linux

```bash
git clone https://github.com/mveysi/watch-youtube-trading.git
cd watch-youtube-trading

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
python -m spacy download en_core_web_sm

# ffmpeg
brew install ffmpeg          # macOS (Homebrew)
sudo apt install ffmpeg      # Ubuntu / Debian

watch-youtube --help         # test
```

---

## 5. İsteğe bağlı: Groq API anahtarı

**Ne işe yarar?** YouTube'un otomatik Türkçe altyazısı, konuşmanın içindeki İngilizce terimleri bozar. Örneğin bir Price Action dersinde "Higher High" altyazıda **"Hayır hayır"**, "Smart Money" **"Smart mani"**, "Price Action" **"Play Station"** olarak çıkar. Groq'un ücretsiz Whisper servisi bu terimleri çok daha doğru yazar.

Örnek ölçüm (30 dakikalık bir ders, terimin doğru yazılma sayısı):

| Terim | YouTube altyazısı | Whisper |
|------|:---:|:---:|
| Smart Money | 0 | 10 |
| Demand | 0 | 14 |
| Price Action | 0 | 4 |

**Alma ve kaydetme:**

1. [console.groq.com](https://console.groq.com) → Google hesabıyla giriş → **API Keys → Create API Key**
2. `gsk_...` ile başlayan anahtarı kopyala ve **ortam değişkeni** olarak kaydet. Anahtarı asla bir dosyaya, koda veya sohbete yazma.

   **Windows (PowerShell):**
   ```powershell
   setx GROQ_API_KEY "gsk_buraya_anahtarin"
   ```
   Sonra VS Code'u / terminali tamamen kapatıp aç. Kontrol: `echo $env:GROQ_API_KEY`

   **macOS / Linux:** `~/.zshrc` veya `~/.bashrc` dosyasına ekle:
   ```bash
   export GROQ_API_KEY="gsk_buraya_anahtarin"
   ```

3. Kullanmak için komuta `--whisper -l tr` ekle (bkz. [bölüm 7](#7-kullanım-2-sadece-komut-satırı)). Claude Code'a "Whisper ile işle" demen de yeterli.

---

## 6. Kullanım 1: Claude Code ile (asıl kullanım)

1. Proje klasörünü **VS Code**'da aç (veya terminalde klasöre girip `claude` yaz).
2. Claude Code sohbetine bir YouTube linki yapıştır:
   ```
   https://www.youtube.com/watch?v=VIDEO_ID
   ```
   Playlist linkleri de olur (`...&list=...&index=3`), sadece o tek video işlenir.
3. Claude, proje kökündeki **`CLAUDE.md`** talimatları sayesinde şunları kendisi yapar:
   - Video daha önce işlendiyse tekrar işlemez, wiki'den cevaplar.
   - İşlenmediyse `watch-youtube` aracını çalıştırır.
   - Storyboard'ları ve tam transcript'i okur, altyazı hatalarını düzeltir.
   - `docs/wiki/` altına konu sayfalarını yazar, `Videos.md` ve `Index.md` dosyalarını günceller.
4. Sonra soru sor:
   ```
   Market yapısında BOS ile MSB arasındaki fark ne?
   ```
   Claude önce wiki'ye bakar ve cevabı hangi sayfadan/videodan aldığını belirtir. Konu wiki'de yoksa sana ilgili bir video linki ister.

> **İlk kullanımda** `docs/wiki/` klasörü yoksa Claude onu `docs/wiki_template/` içindeki boş şablonlardan oluşturur.

**Wiki'yi okumak için:** `docs/wiki/` klasörü [Obsidian](https://obsidian.md/) ile açılırsa sayfalar arası `[[bağlantılar]]` tıklanabilir ve konu haritası grafik olarak görülebilir. Normal bir metin editörüyle de okunabilir.

---

## 7. Kullanım 2: Sadece komut satırı

Claude Code olmadan da kareleri ve transcript'i çıkarabilirsin (wiki yazılmaz):

```powershell
# Windows: önce sanal ortamı etkinleştir
.venv\Scripts\Activate.ps1

# Standart
watch-youtube "https://www.youtube.com/watch?v=VIDEO_ID" -o ./output -v

# Türkçe video + Whisper (Groq anahtarı gerekir)
watch-youtube "https://www.youtube.com/watch?v=VIDEO_ID" -o ./output --whisper -l tr

# Kare sayısını elle belirle
watch-youtube "https://www.youtube.com/watch?v=VIDEO_ID" -o ./output -n 40
```

macOS/Linux'ta önce `source .venv/bin/activate`, komutlar aynı.

İşlem süresi: 10–40 dakikalık bir video için genelde **30 saniye – 2 dakika.**

---

## 8. Çıktılar

Her video için `output/<VIDEO_ID>/` klasörü oluşur (GitHub'a yüklenmez):

| Dosya | İçerik |
|------|--------|
| `storyboard_page_001.jpg`, `002`… | 3×3 kare ızgaraları. Her karenin sol üstünde zaman damgası, altında o an konuşulan metin. |
| `transcript.txt` | Tam transcript, ~30 saniyede bir `[dk:sn]` damgasıyla. Konuşmaya dayalı derslerde asıl bilgi burada. |
| `transcript_raw.vtt` / `transcript_raw.srt` | Ham altyazı dosyası (YouTube ve/veya Whisper) |
| `metadata.json` | Başlık, kanal, süre, transcript kaynağı, her karenin zamanı ve neden seçildiği |

Wiki dosyaları (`docs/wiki/`):

| Dosya | İçerik |
|------|--------|
| `Index.md` | Ana harita: tüm konu sayfalarının listesi |
| `Videos.md` | İşlenmiş videoların kayıt defteri (hangi videodan hangi sayfalar çıktı) |
| `<Konu>.md` | Konu sayfaları. Her birinin başında **Özet, Teknolojiler, Bağlantılar, Kaynak Video** alanları var. Trading konularında ayrıca **"Bot / Uygulama İçin Çıkarılabilir Kurallar"** ve **"Açık sorular"** bölümleri bulunur. |

---

## 9. Tüm seçenekler

| Seçenek | Varsayılan | Açıklama |
|--------|-----------|----------|
| `-o, --output-dir` | `.` | Çıktı klasörü (içinde `<VIDEO_ID>/` oluşturulur) |
| `--frames` | `visual` | `visual`: ekran değişimi tabanlı kare seçimi (önerilen). `transcript`: eski anahtar kelime yöntemi |
| `-n, --max-frames` | otomatik | Kare bütçesi. Otomatik ≈ 35 saniyede 1 kare (en az 12, en fazla 60) |
| `--scene-threshold` | `0.03` | Ekran değişimi hassasiyeti (düşük = daha hassas) |
| `--whisper` | kapalı | YouTube altyazısı olsa bile Groq Whisper kullan |
| `-l, --language` | otomatik | Whisper için konuşma dili (`tr`, `en`…) |
| `--glossary` | `data/glossary_trading_tr.json` | Whisper'a gönderilecek terim listesi dosyası |
| `-k, --groq-api-key` | `GROQ_API_KEY` ortam değişkeni | Groq anahtarı |
| `--learn / --no-learn` | `--no-learn` | Kendi kendine öğrenen anahtar kelime deposunu güncelle |
| `-q, --jpeg-quality` | `85` | Storyboard JPEG kalitesi (1–95) |
| `-g, --silence-gap` | `5.0` | (`transcript` modu) Sessizlik eşiği, saniye |
| `--keep-temp` | kapalı | İndirilen videoyu ve ham kareleri silme |
| `-v, --verbose` | kapalı | Ayrıntılı log |

---

## 10. Proje yapısı

```
├── CLAUDE.md                     # Claude Code'un bu projede nasıl çalışacağını anlatan talimatlar
├── README.md                     # Bu dosya
├── DEGISIKLIKLER.md              # Orijinal projeye göre yapılan değişiklikler
├── YOL_HARITASI.md               # Sıradaki görevler: Whisper düzeltmesi, Playbook, seriyi işleme
├── requirements.txt / setup.py   # Python bağımlılıkları ve kurulum
│
├── watch_youtube/                # Python aracı
│   ├── main.py                   # Komut satırı (watch-youtube) ve akış
│   ├── downloader.py             # yt-dlp ile altyazı/video indirme, Groq Whisper
│   ├── scenes.py                 # Ekran değişimi tespiti ve kare seçimi
│   ├── analyzer.py               # Transcript'ten ipucu çıkarma (TR + EN), öğrenen kelime deposu
│   ├── extractor.py              # ffmpeg ile kare alma, siyah kare eleme
│   └── compiler.py               # Storyboard ızgaralarını oluşturma
│
├── .claude/skills/
│   ├── watch-youtube/SKILL.md    # Claude'un video işleme talimatları
│   └── wiki-schema/SKILL.md      # Wiki sayfası yazma kuralları
│
├── data/
│   ├── glossary_trading_tr.json  # Trading terimleri + bilinen altyazı hataları sözlüğü
│   └── keyword_store.json        # Anahtar kelime deposu
│
├── docs/
│   ├── wiki_template/            # Boş başlangıç wiki'si (ilk kullanımda kopyalanır)
│   └── wiki/                     # Senin wiki'n (GitHub'a yüklenmez)
│
└── output/                       # Storyboard'lar ve transcript'ler (GitHub'a yüklenmez)
```

`docs/wiki/`, `output/`, `.venv/` ve `tools/` klasörleri `.gitignore` ile GitHub dışında tutulur. Herkes kendi wiki'sini kendi videolarından oluşturur.

---

## 11. Teknik detaylar

### Kare seçimi (`--frames visual`, varsayılan)

1. **ffmpeg sahne tespiti** ile görüntünün belirgin değiştiği anlar bulunur.
2. Video bu anlara göre **sabit kesitlere** bölünür. En az 4 saniye değişmeden kalan her kesitin **bitişinden ~1 saniye önceki** karesi alınır. O anda slayt tamamen çizilmiş, açıklamalar eklenmiş olur.
3. Ekranda uzun kalan kesitler (ör. ders sonu özet slaytı) **daha öncelikli** sayılır.
4. ~60 saniyeden uzun boşluklar, transcript'teki "ekranda", "grafikte", "çiziyorum" gibi ipuçlarıyla, yoksa eşit aralıklarla doldurulur.
5. Kare bütçesi aşılırsa, videoyu eşit kapsayacak ve önemli kareleri koruyacak şekilde azaltılır.
6. Tamamen siyah/boş kareler elenir.

Bu yöntem dilden bağımsızdır. Eski yöntem (`--frames transcript`) İngilizce anahtar kelimelere dayandığı için Türkçe videolarda neredeyse hiç kare bulamıyordu.

### Transcript

- Önce YouTube altyazısı (orijinal dil) indirilir.
- `--whisper` verilirse ses düşük bit hızında (mono, 16 kHz, 32 kbps; ~1.5 saate kadar Groq'un 25 MB sınırına sığar) indirilip Groq Whisper'a gönderilir. `data/glossary_trading_tr.json` içindeki terim listesi Whisper'a ipucu olarak verilir.
- Whisper başarısız olursa YouTube altyazısına geri dönülür. İki dosya da saklanır.

### Altyazı hata sözlüğü

`data/glossary_trading_tr.json` → `asr_corrections`: YouTube'un Türkçe altyazısının terimleri nasıl bozduğunun listesi (ör. "Boz" → BOS, "çencu karakter" → CHoCH). Claude wiki yazarken bunu **başvuru rehberi** olarak kullanır. Otomatik değiştirme yapılmaz, çünkü örneğin "hayır" gerçekten "hayır" anlamında da geçebilir. Yeni hatalar görüldükçe listeye eklenir.

### Storyboard ızgarası

| Kare | Izgara | Hücre genişliği |
|---|---|---|
| 1 | 1×1 | 1280px |
| 2 | 2×1 | 1024px |
| 3–4 | 2×2 | 960px |
| 5–6 | 3×2 | 800px |
| 7–9 | 3×3 | 720px |
| 10+ | 3×3'lük sayfalar | 720px |

### Python bağımlılıkları

| Paket | Amaç |
|---|---|
| `yt-dlp` | YouTube altyazı + video indirme |
| `Pillow` | Storyboard ızgarası |
| `spaCy` | Transcript dil işleme |
| `scikit-learn` | Öğrenen kelime deposu (TF-IDF) |
| `webvtt-py` | VTT altyazı okuma |
| `click` | Komut satırı |
| `groq` | Whisper API |

---

## 12. Sorun giderme

| Hata / Belirti | Çözüm |
|---|---|
| `watch-youtube` komutu bulunamadı | Sanal ortam etkin değil: Windows `.venv\Scripts\Activate.ps1`, mac/Linux `source .venv/bin/activate`. Sonra `pip install -e .` |
| `running scripts is disabled` (PowerShell) | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `ffmpeg not found` | Windows `winget install Gyan.FFmpeg` (sonra terminali yeniden aç), macOS `brew install ffmpeg`, Ubuntu `sudo apt install ffmpeg` |
| `UnicodeEncodeError` | Windows: `setx PYTHONIOENCODING utf-8` ve terminali yeniden aç |
| `No module named spacy` / model hatası | `pip install -r requirements.txt` ve `python -m spacy download en_core_web_sm` |
| `HTTP Error 429` (İngilizce altyazı) | Zararsız. Orijinal dildeki altyazı indiyse işlem devam eder. |
| `No supported JavaScript runtime` uyarısı | Şimdilik zararsız. İndirmeler bozulursa [deno](https://deno.com/) kur. |
| `Cannot access video` | Video gizli, yaş kısıtlamalı veya bölge engelli olabilir |
| `--whisper` çalışmıyor | `GROQ_API_KEY` tanımlı mı? (Windows: `echo $env:GROQ_API_KEY`). `setx` sonrası terminal yeniden açılmalı. |
| Whisper: "over Groq's 25 MB limit" | Video ~1.5 saatten uzun; `--whisper` olmadan YouTube altyazısıyla çalıştır |

---

## 13. Bilinen sınırlamalar

- **Konuşan kafa videolarında kısa ekran yazıları kaçabilir.** Arka planda renk değiştiren ışıklar ve el hareketleri çok sayıda sahte "sahne değişimi" üretir. 10–20 saniyelik alt yazılar kare aralarına düşebilir. Bu bilgiler genelde konuşmada da geçtiği için `transcript.txt` bunu telafi eder. Daha fazla kare için `-n` değerini artır.
- **Whisper uzun seslerde bazen tekrar döngüsüne girer** ("BASE BASE BASE…") veya kısa bölümleri boş bırakır. YouTube altyazısı da saklandığı için Claude bu kısımları oradan tamamlar.
- **Otomatik altyazı hataları** Whisper olmadan sadece kısmen düzeltilebilir (sözlük + ekran görüntüleri + bağlam ile).
- Wiki'deki bilgiler videolardaki anlatımın notlarıdır; doğrulanmış yatırım tavsiyesi değildir. Bir stratejiyi kullanmadan önce mutlaka test et (backtest).

---

## 14. Teşekkür

Bu proje, **Oğuzcan Karaman**'ın [Watch_Youtube_Skill](https://github.com/oguzcankaraman/Watch_Youtube_Skill) projesi üzerine geliştirilmiştir (orijinal pipeline, storyboard yaklaşımı ve wiki-schema yapısı). Bu sürümde yapılan değişiklikler için: [DEGISIKLIKLER.md](DEGISIKLIKLER.md)

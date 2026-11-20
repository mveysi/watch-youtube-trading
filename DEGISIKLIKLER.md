# Değişiklikler

Bu sürüm, [oguzcankaraman/Watch_Youtube_Skill](https://github.com/oguzcankaraman/Watch_Youtube_Skill) projesinin (commit `41a634d`) üzerine yapılan iyileştirmeleri içerir. Amaç özellikle **Türkçe** ve **grafik/slayt ağırlıklı ders videolarında** (ör. trading eğitimleri) aracın doğru çalışmasını sağlamaktı.

Kurulum ve kullanım için: [README.md](README.md)

## Neden?

Orijinal sürüm Türkçe bir Price Action eğitim serisinde test edildiğinde:
- Kare seçimi İngilizce anahtar kelimelere dayandığı için **37 dakikalık grafikli bir derste sadece 5 eşit aralıklı kare** alındı; ilk kare siyah ekrandı, ders slaytlarının çoğu kaçtı.
- Playlist linklerinde (`&list=...`) **yanlış videonun** altyazısı işlendi.
- Kendi kendine öğrenen kelime deposu **"yani", "böyle", "bir tane"** gibi kelimeler öğreniyordu.
- Windows'ta Türkçe karakterler storyboard'da kutu olarak çıkıyordu.
- Transcript iş bitince siliniyordu.

Bu sorunların hepsi giderildi ve 4 farklı video (konuşan kafa, slayt, grafik) üzerinde test edildi.

## Neler değişti

### Yeni dosyalar

| Dosya | Açıklama |
|------|----------|
| `watch_youtube/scenes.py` | **Yeni kare seçme motoru.** ffmpeg sahne değişimi tespiti ile videoyu "sabit kesitlere" böler ve her kesitin **son halini** alır (slayt tamamen çizilmiş haliyle). Uzun süre ekranda kalan kesitler öncelikli. Uzun boşluklar (>~60 sn) transcript ipuçlarıyla veya eşit aralıkla doldurulur. Dilden bağımsız çalışır. |
| `data/glossary_trading_tr.json` | Trading terim sözlüğü. `whisper_prompt` alanı Groq Whisper'a kelime ipucu olarak gider. `asr_corrections` alanı YouTube'un Türkçe otomatik altyazısının İngilizce terimleri nasıl bozduğunu listeler (ör. "Hayır hayır" = Higher High, "Boz" = BOS, "Play Station" = Price Action). Wiki yazarken başvuru kaynağı olarak kullanılır, otomatik uygulanmaz. |

### Değişen dosyalar

| Dosya | Değişiklik | Neden |
|------|-----------|-------|
| `watch_youtube/main.py` | Akış 5 adıma çıktı. Yeni seçenekler: `--frames visual\|transcript`, `--whisper`, `--language`, `--glossary`, `--scene-threshold`, `--learn/--no-learn`. `--max-frames` artık video süresine göre otomatik (≈35 sn'de 1 kare, 12–60). Transcript ve `metadata.json` kalıcı kaydediliyor. HTTP kütüphanelerinin log gürültüsü kısıldı. | Eski sistem Türkçe videolarda hiç anahtar kelime bulamayıp **5 eşit aralıklı kareye** düşüyordu. 37 dakikalık grafikli bir derste ders slaytlarının çoğu kaçıyordu. Transcript iş bitince siliniyordu. |
| `watch_youtube/downloader.py` | (1) **Playlist düzeltmesi:** link her zaman `watch?v=ID` biçimine indiriliyor + `noplaylist`. (2) Video başlığı, kanal ve süre alınıyor. (3) `--whisper`: YouTube altyazısı olsa bile Groq Whisper kullan, glossary ipucuyla. Başarısız olursa YouTube altyazısına geri dön. (4) Ses mono 16 kHz 32 kbps indiriliyor (Groq'un 25 MB sınırı için). (5) Groq SDK'nın segmentleri dict olarak döndürdüğü sürümle uyumluluk. | `&list=...` içeren linklerde yanlış videonun transcript'i alınıyordu. Türkçe konuşma içindeki İngilizce terimler YouTube altyazısında anlamsız kelimelere dönüşüyordu. |
| `watch_youtube/analyzer.py` | Türkçe "gösterme" ifadeleri eklendi ("ekranda", "grafikte", "çiziyorum", "işaretliyorum"…). Yeni `trading` kelime grubu (destek, direnç, trend, BOS, MSB…). Türkçe gereksiz kelime (stopword) listesi. Kendi kendine öğrenme artık sadece gerçek anahtar kelime karelerinden öğreniyor (yedek/sahne karelerinden değil). Depo UTF-8 okunup yazılıyor. Koddaki yerleşik kelimeler eski depolara otomatik ekleniyor. | Öğrenme sistemi "yani", "böyle", "bir tane" gibi çöp kelimeler öğreniyordu. Bunlar 3 videoda görülünce ağırlıkları 0.8'e çıkıp neredeyse her cümlede kare aldıracaktı. |
| `watch_youtube/extractor.py` | Siyah/boş kareler (ortalama parlaklık < 12) eleniyor. | Videonun ilk karesi genelde siyah oluyordu. |
| `watch_youtube/compiler.py` | Windows yazı tipleri eklendi (`segoeui.ttf`, `arial.ttf`). | Windows'ta Pillow varsayılan yazı tipine düşüyordu ve Türkçe karakterler (ş, ğ, ı, İ) kutu olarak çıkıyordu. |
| `watch_youtube/__init__.py` | `DownloadResult` sınıfına `transcript_path`, `title`, `channel`, `duration` alanları eklendi. | Meta veri ve transcript kaydı için. |
| `data/keyword_store.json` | **Temizlendi:** önceki test videolarından öğrenilmiş alakasız kelimeler ("kernel", "claude code"…) silindi, sadece yerleşik kelimeler kaldı (59 adet). | Kirlenmiş depo yanlış karelerin seçilmesine yol açıyordu. |
| `.claude/skills/watch-youtube/SKILL.md` | Baştan yazıldı: Windows kurulum/çalıştırma komutları, tüm yeni seçenekler, çıktı dosyaları, **storyboard'larla birlikte `transcript.txt`'yi de oku** kuralı, altyazı düzeltme süreci, kapsam kontrolü (kaçan slayt var mı), trading sayfaları için **"Bot / Uygulama İçin Çıkarılabilir Kurallar"** ve **"Açık sorular"** bölümleri. | Eski talimat sadece storyboard'u okumayı söylüyordu ve yolları macOS'a göreydi. |
| `CLAUDE.md` | "CLI Kullanımı" bölümüne Windows komutları ve çıktı dosyaları eklendi. | — |

---

## Ek: Repo düzenlemeleri

- `README.md` yeni başlayanlar için baştan yazıldı (Windows + macOS/Linux kurulumu, Groq, kullanım, sorun giderme).
- `docs/wiki_template/`: boş başlangıç wiki'si; `docs/wiki/` GitHub'a yüklenmediği için ilk kullanımda Claude bunu kopyalar.
- `.gitignore`: `tools/` (ffmpeg) ve `*.egg-info/` eklendi; `.gitattributes` ile satır sonları LF'ye sabitlendi.

## Ek 2: Eğitim fazı hazırlığı (2026-11-20)

6 video üzerinde test edilerek eklendi:

| Değişiklik | Neden |
|-----------|-------|
| **Whisper parçalama** (10 dk) + `transcript_repair.py` | Tek parça seste Whisper ~%25 konuşmayı sessizce atlıyor, döngüye giriyordu. Ayrıca Türkçe harflerde kelimeleri kesiyor ("Buras", "ger") veya İngilizceye çeviriyordu. Bozuk bölümler tespit edilip aynı dildeki YouTube altyazısıyla doldurulur (`[yt]`). |
| **Whisper ipucu kısa doğal cümle** | 728 karakterlik terim listesi Whisper'ı tamamen bozdu (10 dk'dan 277 anlamsız kelime). Kodda 250 karakter sınırı + uyarı. |
| **Orijinal dil seçimi** (altyazı + ses) | YouTube'un otomatik dublajlı videolarında `en-US-orig` dublaj altyazısı `tr-orig` yerine seçiliyordu. Artık videonun orijinal dili meta veriden okunuyor. |
| **Video indirme doğrulaması** | `android` istemcisi bir derste 23 dakikalık video için 583 KB'lık yarım dosya verdi (0 kare). Önce varsayılan istemci, sonra yedek; dosya sonundan kare okunarak doğrulanıyor. H.264 tercih ediliyor (AV1 sahne tespitinde çok yavaş). |
| **Sıfır kare = hata** | Önceden kare çıkarılamazsa program "başarılı" diyordu. |
| **Playbook** (`docs/wiki_template/Playbook.md`, `docs/playbook_ornek.md`) + SKILL.md adımları | Kuralların ID'li, kaynaklı, ölçülebilir tek listesi; açık sorular ve çelişkiler tablosu; her videodan sonra Kalite Raporu. |
| Gemini incelemesinden 5 düzeltme | Orijinal dil altyazı önceliği, VTT tekrar filtresi, Türkçe ek eşleşmesi, satır kaydırma hatası, sahne tespiti 640px. |


## Ek 3: Bilgi biriktiren sistem (2026-11-20)

Amaç dersleri tek tek özetlemek değil, seri ilerledikçe tek ve tutarlı bir bilgi modeli kurmak (seri 20+ saat ve her ders öncekinin üstüne inşa ediliyor).

| Değişiklik | Neden |
|-----------|-------|
| **`playbook-check` komutu** (`watch_youtube/playbook_check.py`) | Playbook'u denetler: çift kural ID'si, eksik/geçersiz alan, tanımsız kural/soru atfı, kırık `[[Videos#ID]]` linki, `?` parametresi olup sorusu olmayan kural. `--write` ile Playbook başındaki **Bilgi Durumu** panosunu (kategori bazında aktif / koda hazır kural, soru durumları, bekleyen çelişki) üretir; `--last-log` öğrenme günlüğünün sadece son kaydını yazar. 20+ saatlik seride sessiz format bozulmasını önler. |
| **`LearningLog.md`** (şablon) | Her dersin ne kattığı (yeni / inceltilen / kapanan soru / yeni soru / bilgi durumu). Sadece sona eklenir, baştan okunmaz (bağlam yükü olmasın). Videos.md'ye konmadı, çünkü Videos.md her URL sorusunda okunuyor. |
| **Ders öncesi aktif öğrenme** (SKILL.md) | Claude dersi okumadan önce açık/beklenen soruları ve ilgili kuralları okur; yeni bilgiyi yeni / inceltme / çelişki olarak sınıflandırır. |
| **`beklenen` soru durumu** | Eğitmen "ileride anlatacağım" derse soru kaydedilir ve o ders gelince kapanır. |
| **Değişiklik yayılımı** (SKILL.md) | Bir kural değişince İlgili kurallar ve onu kullanan tüm sayfalar/kod taslakları düzeltilir. |
| **Kavram sayfası formatı** (wiki-schema §6) | Ana metin hep güncel bilgiyi anlatır; değişiklikler sondaki "Tanımın Gelişimi" bölümüne tek satır. Derse özgü içerik (ödevler, ders sonu slaytı) Videos.md kaydına gider. 500 kelime sınırı → güncel içerik ~1000 kelime (gelişim bölümü sayılmaz). |
| **Playbook kabul filtresi** | Sadece bir programın hesaplama/karar için ihtiyaç duyduğu şeyler kural ID'si alır (tanım, filtre, giriş/stop/hedef, risk); anekdot ve yorumlar konu sayfasında kalır. Kural şişmesini önler. |
| **Çelişki ilkesi** | Önerilen varsayılan: aynı eğitmenin sonraki, konuya özel dersi; karar yine kullanıcıda. |
| **ffmpeg otomatik bulma** (`extractor.py`) | PATH'te yoksa proje içindeki `tools/**/ffmpeg(.exe)` aranır (sürüm klasörü adı önemsiz) ve PATH'e eklenir; ffprobe de oradan bulunur. Başka bir bilgisayarda sabit `ffmpeg-9.0.2` yolu yüzünden hata çıkmaz. |
| **YouTube çerez desteği** (`--cookies`, `--cookies-from-browser`, `./cookies.txt` otomatik) | Çok sayıda indirmeden sonra YouTube IP'yi "bot değilim" doğrulamasıyla engelledi (tüm videolar, tüm istemciler). Çerezler sadece okunur; `cookies*.txt` gitignore'da. |

### Ek 3 düzeltmeleri (Gemini incelemesi sonrası)

| Düzeltme | Neden |
|---------|-------|
| `transcript_repair`: sadece gerçekten doldurulan bölüm sayısı döner | YouTube altyazısı yokken silinen bölümler için de "N bölüm YouTube altyazısıyla dolduruldu" notu yazılıyordu. |
| Çerez varken altyazı adımında `android` istemcisi zorlanmaz | `android` istemcisi çerezi desteklemiyor; bot engelinde çerezle çalışırken altyazı alınamayabilirdi. |
| `playbook-check`: çelişki "açık" sayılması esnetildi (boş / `⏳` / "bekleniyor"); `✅`/`⏳` kuralı şablon ve SKILL'e yazıldı; HTML yorumları denetimden hariç | `✅` ile başlamayan kararlar sürekli açık görünüyordu; şablondaki örnek yorum gereksiz uyarı üretiyordu. Boş şablon artık 0 uyarı. |
| Index şablonuna `[[LearningLog]]`; 25 MB notları güncellendi | Ses 10 dk'lık parçalarla gönderildiği için 25 MB sınırı pratikte aşılmıyor. |

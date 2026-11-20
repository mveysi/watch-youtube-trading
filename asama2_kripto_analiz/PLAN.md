# Aşama 2: Kripto Analiz Motoru (Plan)

> **Kime:** Bu planı kendi bilgisayarında Claude Code ile uygulayacak kişiye ve onun Claude'una.
> **Başlatmak için:** Claude Code'a şunu yaz: *"asama2_kripto_analiz/PLAN.md ve asama2_kripto_analiz/CLAUDE.md dosyalarını oku, Adım 0'dan başla."*
> **Durum:** Sadece plan. Henüz kod yok. (Plan tarihi: 2026-11-20)

---

## 1. Amaç

Aşama 1'de YouTube derslerinden öğrenilen işlem kuralları `docs/wiki/Playbook.md` dosyasında ID'li ve ölçülebilir olarak tutuluyor. Aşama 2'nin amacı bu kuralları **mum (OHLCV) verisi üzerinde Python ile hesaplamak**: swing noktaları, trend, BOS/MSB/CHoCH, imbalance…

Neden: Claude'un grafik ekran görüntüsüne bakıp "göz kararı" yorum yapması tutarsız sonuç veriyor (backtest'te işlem kaçırma sorununun bir nedeni). Sayısal motor aynı veride **her seferinde aynı** sonucu verir; Claude sonra bu sonuçları yorumlar.

## 2. Sınırlar (kesin)

- **Gerçek emir yok.** Bu aşamada borsaya emir gönderen hiçbir kod yazılmaz. İşlem yetkili API anahtarı kullanılmaz; sadece halka açık (anahtarsız) piyasa verisi okunur.
- **Aşama 1'e dokunulmaz.** `watch_youtube/`, `.claude/skills/`, `docs/wiki_template/`, kök `README.md`/`CLAUDE.md` değiştirilmez. Aşama 2'nin tüm kodu, testi ve çıktısı `asama2_kripto_analiz/` içinde kalır. Aşama 1'den tek alınan şey `docs/wiki/Playbook.md` (sadece **okunur**).
- **Ayrı dal.** Çalışma `asama-2` git dalında yapılır. `main`'e birleştirme kullanıcının onayıyla olur.
- **Henüz öğretilmemiş kural kodlanmaz.** Playbook'ta olmayan bir konu (ör. order block sınırları) "tahminle" eklenmez. Motor, Playbook büyüdükçe büyür.

## 3. Önemli: Kural ID'leri senin Playbook'una göre

Bu planda geçen kural ID'leri (MS-001, IMB-001…) planı hazırlayanların **pilot** Playbook'undan (1–6. dersler) alınmıştır. Sen seriyi baştan işlediğin için senin Playbook'unda numaralar farklı olabilir. **Her zaman kendi `docs/wiki/Playbook.md` dosyandaki ID'leri ve tanımları esas al.** Aşağıdaki "pilot tanımlar" sadece neyin kodlanacağını anlatmak içindir.

---

## 3b. Plan ayrı indirildiyse

Bu plan `asama2-plan` dalından tek başına da indirilebilir. Okumak için yeterlidir; **uygulamak** için Aşama 1'in çıktılarına erişim gerekir: `docs/wiki/Playbook.md` (kurallar) ve `output/oQhdnKzsGyw/` (eğitmenin BTC grafiği kareleri). İki yol:
- **Önerilen:** tam repoyu klonla, `asama-2` dalında bu klasörde çalış.
- **Ayrı proje olarak:** planı kendi klasöründe uygula; Aşama 1 klasörünün yerini ayar olarak ver (`playbook_yolu`, `storyboard_klasoru`). Kurallar yine o Playbook'tan okunur, kopyalanıp elle değiştirilmez.

## 4. Klasör yapısı (hedef)

```
asama2_kripto_analiz/
├── PLAN.md                 # bu dosya
├── CLAUDE.md               # Claude için çalışma kuralları (bu klasöre özel)
├── README.md               # kısa tanıtım + nasıl çalıştırılır
├── requirements.txt        # Aşama 2'nin kendi bağımlılıkları (Aşama 1'den bağımsız)
├── beklenen/               # kod yazılmadan ÖNCE dondurulan doğru cevaplar (kabul testi)
│   └── btc_1d_2021_2022.md
├── market_analysis/        # Python paketi
│   ├── data.py             # mum verisi: Binance / yedek kaynak / CSV + önbellek
│   ├── params.py           # açık sorulara bağlı ayarlar
│   ├── structure.py        # swing, HH/HL/LH/LL, trend, BOS/MSB/CHoCH, korunması gereken seviye
│   ├── imbalance.py        # 3 mum imbalance + doldurulma takibi
│   ├── chart.py            # etiketli grafik resmi (görsel kontrol için)
│   └── cli.py              # `python -m market_analysis ...` komutu
├── tests/                  # kural bazlı birim testler + kabul testi
└── ciktilar/               # grafikler, raporlar, veri önbelleği (GitHub'a yüklenmez)
```

---

## 5. Güven protokolü (her adımda geçerli)

Testi yazan ile sonucu "geçti" diyen aynı Claude olursa sonuca güvenilmez. Bu yüzden:

1. **Doğru cevap koddan önce yazılır ve dondurulur.** `beklenen/` altındaki dosyalar eğitmenin kendi işaretlemelerinden çıkarılır, kullanıcı onaylar, **ayrı bir commit** olarak kaydedilir. Kod yazıldıktan sonra bu dosyalar **değiştirilmez** (değişmesi gerekirse kullanıcıya sorulur ve nedeni commit mesajına yazılır).
2. **Görsel kanıt.** Motor her kabul testinde etiketli bir grafik resmi üretir. Kullanıcı bunu eğitmenin ekran görüntüsüyle (Aşama 1'in `output/<video_id>/storyboard_page_*.jpg` dosyaları) **yan yana** karşılaştırır.
3. **Uyuşmazlık saklanmaz.** Rapor her beklenen nokta için "tuttu / tutmadı / kısmen" yazar; tutmayanların nedenini açıklar. "Tamamen geçti" ancak hepsi tuttuysa denir.
4. **Ezber yasak.** Ayarlar tek bir grafiğe göre aşırı ayarlanmaz: ayarlar BTC örneğinde seçildiyse, başka bir örnekte (eğitmenin Forex örneği veya sonraki derslerdeki grafikler) de denenir ve sonuç ayrıca raporlanır.
5. **Bağımsız tekrar.** Aynı komut başka bir bilgisayarda (ör. planı hazırlayan kullanıcı tarafında, Yahoo verisiyle) çalıştırıldığında aynı olaylar çıkmalıdır.

---

## 6. Adımlar

Her adımın bir **kabul kriteri** var. Kriter sağlanmadan sonraki adıma geçilmez. Bir yöntem tutmazsa **"Olmazsa"** satırındaki alternatif denenir; hiçbiri tutmazsa durulur ve kullanıcıya sorulur.

### Adım 0: Beklenen noktaları dondur (kod yok)

- 2. dersin (`oQhdnKzsGyw`, "Market Yapısını Anlamak") 26:21–32:45 bölümünde eğitmen günlük BTC grafiğinde (2021 – Mart 2022) trendi çiziyor ve dönüş noktalarını etiketliyor. Kareler: `output/oQhdnKzsGyw/storyboard_page_004.jpg` ve `005.jpg` (yaklaşık 1640–1954 sn). Transcript: `output/oQhdnKzsGyw/transcript.txt`.
- `beklenen/btc_1d_2021_2022.md` dosyasında **aday** bir liste hazır (planı hazırlayanın storyboard + transcript + Yahoo verisinden çıkardığı tahminler). Bunları storyboard karelerine ve gerçek mum verisine bakarak **doğrula**, tarihleri düzelt, belirsizleri "belirsiz" diye işaretle.
- **Kabul:** kullanıcı listeyi onaylar → dosyanın başındaki durum `ONAYLANDI (tarih)` olur → ayrı commit.
- **Olmazsa:** storyboard'da etiket okunamıyorsa video tekrar işlenebilir (`watch-youtube <URL> -o ./output -n 60 --keep-temp`) veya o dakikadan tek kare alınabilir (`ffmpeg -ss 1700 -i video.mp4 -frames:v 1 kare.jpg`).

### Adım 1: Veri katmanı (`data.py`)

- **Binance** halka açık mum verisi: `GET https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&startTime=<ms>&endTime=<ms>&limit=1000`. Tek istekte en fazla 1000 mum; daha uzun aralık için `startTime` ilerletilerek sayfalanır. Dönen dizi: `[açılış_zamanı_ms, open, high, low, close, volume, kapanış_zamanı_ms, …]` (sayılar metin olarak gelir → float'a çevir). Zaman **UTC**.
- Yedek kaynaklar: Binance'in toplu arşivi `https://data.binance.vision/` (günlük/aylık zip CSV), Yahoo Finance (`BTC-USD`), elle indirilmiş CSV (ör. TradingView dışa aktarımı).
- Önbellek: `ciktilar/veri/<kaynak>_<sembol>_<aralık>.csv`; aynı aralık tekrar istenirse internete çıkılmaz.
- **Kabul:** `python -m market_analysis veri BTCUSDT 1d --from 2021-01-01 --to 2022-03-31` → 455±1 günlük mum; 2021-04-14 high ≈ 64.8–64.9 bin, 2021-11-10 high ≈ 68.8–69.0 bin (kaynağa göre küçük fark normal).
- **Olmazsa:** API erişimi yoksa (bazı ağlarda kripto siteleri engelli) `data.binance.vision` → Yahoo → CSV sırasıyla dene; hangi kaynağın kullanıldığını her çıktıya yaz.

### Adım 2: Ayarlar (`params.py`)

Eğitmenin henüz sayı vermediği her yer bir **ayar** olur; koda gömülmez. Her ayarın yanında bağlı olduğu Playbook sorusu ve "varsayılan, eğitmen kesinleştirmedi" notu yazar. Pilot Playbook'taki karşılıkları:

| Ayar | Seçenekler | Pilot soru |
|------|-----------|-----------|
| `swing_yontemi` | `fraktal` (sol/sağ N mum) · `zigzag` (% eşik) · `atr` (ATR katı) | Q-001 |
| `swing_n` / `zigzag_yuzde` / `atr_kat` | sayılar | Q-001 |
| `kirilim_tipi` | `kapanis` (gövde kapanışı) · `fitil` | Q-002 |
| `esit_tolerans` | fiyatın %'si | Q-005 |
| `min_imbalance` | fiyatın %'si veya ATR katı | Q-014 |

- **Kabul:** ayarlar tek bir dosyadan (ör. `ayarlar.json`) okunur; komut satırından değiştirilebilir; her çıktı hangi ayarlarla üretildiğini yazar.

### Adım 3: Market yapısı (`structure.py`)

Pilot tanımlar (kendi Playbook'undaki güncel hâlini esas al):

- **Swing ve etiket (MS-001):** yeni swing high > önceki swing high → HH, değilse LH; yeni swing low > önceki swing low → HL, değilse LL.
- **Trend (MS-002):** HH+HL → BOĞA, LH+LL → AYI, ikisi de yoksa YATAY.
- **BOS (MS-003):** trend yönünde son swing'in kırılması (BOĞA'da son swing high, AYI'da son swing low). Kırılım `kirilim_tipi` ayarına göre (kapanış/fitil).
- **Korunması / kırılması gereken seviye (MS-008):** BOĞA'da korunması gereken dip = son HH'yi yaptıran impulsun **başladığı** dip; kırılması gereken tepe = son HH. Her BOS'ta güncellenir. AYI'da tersi.
- **MSB (MS-004):** trende ters **yerel** kırılım (BOĞA'da son HL'nin altına inme). **Trendi çevirmez.**
- **CHoCH (MS-009):** korunması gereken seviyenin kırılması → trend döner. (Ders 2 MSB'yi CHoCH ile eş anlamlı kullanıyordu; Ders 5 ayırdı; kullanıcı kararıyla Ders 5 geçerli.)
- **Mitigasyon (MS-010):** fiyat iki seviye arasındayken yapılan hareketler.
- Eğitmenin vurguladığı tuzak (MS-005): AYI → BOĞA dönüşü için kırılması gereken tepe, **son LL'yi başlatan hareketin tepesidir**; daha yakın küçük bir tepenin kırılması dönüş değildir. BTC örneğinde tam bu durum var ("Market bu bölgeden düşmeye devam edebilirdi").
- Çıktı: olay listesi `[tarih, olay (HH/HL/LH/LL/BOS/MSB/CHoCH), fiyat, trend_önce, trend_sonra, kural_id]`. Her olay hangi Playbook kuralına dayandığını taşır.
- **Birim testler:** her kural için elle kurulmuş, cevabı kağıt üzerinde belli 5–15 mumluk diziler (ör. "HH, HL, HH, sonra korunması gereken dibin altında kapanış → CHoCH, trend AYI"). Ayrıca: yakın küçük tepe kırılınca trend **dönmemeli** (MS-005 tuzağı).
- **Kabul:** tüm birim testler geçer; aynı veride iki çalıştırma aynı olayları verir.
- **Olmazsa:** fraktal swing'ler çok gürültülüyse `zigzag` veya `atr` yöntemine geç; üçü de eğitmenin swing'lerini yakalamıyorsa swing'leri **zaman dilimine göre** ayrı ayrı değerlendir (eğitmen: "hangi zaman diliminde işlem alıyorsan o zaman dilimindeki trend") ve kullanıcıya sor.

### Adım 4: Imbalance (`imbalance.py`)

- **Tanım (IMB-001):** i ortadaki büyük mum olmak üzere `low[i+1] > high[i−1]` → yükseliş imbalance'ı, bölge `[high[i−1], low[i+1]]`; `high[i+1] < low[i−1]` → düşüş imbalance'ı, bölge `[high[i+1], low[i−1]]`. Art arda büyük mumlar tek başına imbalance değildir (IMB-002).
- **Doldurulma (IMB-003):** fiyat bölgeye geri döndü mü, tamamen mi kısmen mi (kısmi dolum kuralı açık soru: Q-013 → ayar).
- **Kabul:** birim testler + BTC verisinde bulunan imbalance'ların grafikte görsel kontrolü.

### Adım 5: Grafik (`chart.py`)

- Mum grafiği + swing etiketleri (HH/HL/LH/LL) + BOS/MSB/CHoCH çizgi ve etiketleri + trend rengi (BOĞA yeşil, AYI kırmızı; eğitmenin renkleri) + imbalance kutuları. Logaritmik ölçek seçeneği (eğitmen HTF'de log ölçek istiyor).
- Çıktı: `ciktilar/grafik_<sembol>_<aralık>_<tarih>.png` (veya etkileşimli HTML).
- **Kabul:** kullanıcı resmi açıp etiketleri okuyabiliyor.
- **Olmazsa:** `mplfinance` → `matplotlib` elle çizim → `plotly` HTML.

### Adım 6: Kabul testi ve kalibrasyon

- Motoru BTC 1d 2021-01-01 – 2022-03-31 verisinde çalıştır; `beklenen/btc_1d_2021_2022.md` ile karşılaştır.
- Ayar kombinasyonlarını tara (ör. swing yöntemi × N × kırılım tipi) ve her kombinasyon için "beklenen noktaların kaçı tuttu" tablosu çıkar.
- Rapor: `ciktilar/kabul_raporu.md` → tablo + en iyi kombinasyon + tutmayan noktaların açıklaması + grafik resmi.
- **Ezber kontrolü:** seçilen ayarları başka bir örnekte de dene (2. dersin Forex örneği, 32:45–34:43; veya sonraki derslerdeki grafikler) ve sonucu ayrıca yaz.
- **Kabul:** kullanıcı grafiği eğitmenin ekran görüntüsüyle yan yana inceleyip onaylar. Önerilen ayarlar Playbook'a **türetilmiş** cevap önerisi olarak not edilir (Playbook'u değiştirmeden önce kullanıcıya sorulur; eğitmen ileride kesin söylerse o geçerli olur).

### Adım 7: Teslim

- `asama2_kripto_analiz/README.md`: kurulum (`pip install -r asama2_kripto_analiz/requirements.txt`), örnek komutlar, çıktılar.
- `asama-2` dalına push; kullanıcıya kabul raporu ve grafik gönderilir.

---

## 7. Bu planın kapsamı dışında (sonraki adımlar)

Sıra, Aşama 1'de ilgili dersler işlenip açık sorular kapandıkça belirlenir:

- Arz/talep bölgeleri (base'in sayısal tanımı henüz yok), order block sınırları, likidite seviyeleri ve sweep
- Çoklu zaman dilimi (HTF trend + LTF giriş)
- Giriş/stop/hedef kuralları → **backtest** (geçmiş veride işlem simülasyonu)
- **Kâğıt üzerinde işlem** (paper trading, gerçek para yok)
- Claude'un motor çıktısını okuyup yorum yaptığı bir analiz skill'i
- Gerçek emir: ancak backtest ve kâğıt işlem sonuçları ikna edici olursa, ayrıca konuşularak

## 8. Takılırsan

- Playbook'ta bir kural koda dökülemeyecek kadar belirsizse: kodlama, `?` olarak bırak, kullanıcıya sor (gerekirse Aşama 1'de açık soru olarak kayıtlı mı kontrol et).
- Bir yöntem iki denemede de kabul kriterini sağlamıyorsa: "Olmazsa" satırına geç; o da olmazsa ne denendiğini ve sonuçlarını yazıp kullanıcıya sor. Kabul kriterini gevşetme.

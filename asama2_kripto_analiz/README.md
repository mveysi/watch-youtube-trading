# Aşama 2: Kripto Analiz Motoru

> **Durum:** Plan aşamasında, henüz kod yok.

Proje iki aşamadan oluşur:

| Aşama | Ne yapar | Nerede |
|------|----------|--------|
| **Aşama 1: Öğrenme** | YouTube ders videolarını izler, öğrenilen işlem kurallarını `docs/wiki/Playbook.md` içinde ID'li ve ölçülebilir olarak biriktirir | Repo kökü (`watch_youtube/`, `.claude/skills/`, `docs/`) |
| **Aşama 2: Analiz** | Playbook'taki kuralları kripto mum verisi (Binance) üzerinde Python ile hesaplar: swing, trend, BOS/MSB/CHoCH, imbalance… Claude'un grafiğe "göz kararı" bakması yerine her seferinde aynı sonucu veren sayısal motor | Bu klasör |

Aşama 2, Aşama 1'in koduna dokunmaz; sadece `docs/wiki/Playbook.md` dosyasını okur.

## Sadece planı indirmek

Repo sayfasında dal seçicisinden **`asama2-plan`** dalını seç → **Code → Download ZIP**. Bu dal sadece bu klasörü içerir. Komut satırından:

```bash
git clone -b asama2-plan --single-branch https://github.com/mveysi/watch-youtube-trading.git asama2-plan
```

Planı uygulamak için Aşama 1'in çıktılarına da erişim gerekir (bkz. [PLAN.md](PLAN.md) §3b).

## Nasıl başlanır

1. Repoyu güncelle ve ayrı dala geç:
   ```bash
   git pull
   git checkout -b asama-2
   ```
2. **Korumayı aç (bir kez):** `asama2_kripto_analiz/kurulum/settings.local.json.ornek` dosyasını `.claude/settings.local.json` adıyla kopyala. Bu, Claude'un ANAYASA'yı, koruma düzeneğini ve Aşama 1 kodunu düzenlemesini ve `main`'e doğrudan push etmesini **teknik olarak engeller**.
   ```bash
   cp asama2_kripto_analiz/kurulum/settings.local.json.ornek .claude/settings.local.json
   ```
   (Zaten bir `.claude/settings.local.json` varsa üzerine yazma; içindeki `deny` listesini mevcut dosyaya ekle.)
3. Claude Code'a şunu yaz:
   *"asama2_kripto_analiz/PLAN.md ve asama2_kripto_analiz/CLAUDE.md dosyalarını oku, Adım 0'dan başla."*
4. Claude her adımın sonunda kanıtıyla (test çıktısı, grafik resmi) rapor verir. İlk iş (Adım 0) eğitmenin BTC grafiğindeki dönüş noktalarını **kod yazılmadan önce** onaylamandır: [beklenen/btc_1d_2021_2022.md](beklenen/btc_1d_2021_2022.md).

## Dosyalar

- [PLAN.md](PLAN.md): amaç, sınırlar, güven protokolü, adımlar ve kabul kriterleri, "olmazsa" alternatifleri
- [ANAYASA.md](ANAYASA.md): **değiştirilemez çekirdek**: sınırlar, güven protokolü, korunan dosyalar
- [CLAUDE.md](CLAUDE.md): Claude'un bu klasörde uyacağı kurallar
- [DEVAM.md](DEVAM.md): devam notu (compact / yeni oturum sonrası otomatik okunur)
- [koruma_kontrol.py](koruma_kontrol.py): korunan dosyalar değişti mi? (GitHub'da her push'ta otomatik çalışır)
- [beklenen/](beklenen/): kabul testinin doğru cevapları (koddan önce dondurulur)

## Koruma (4 katman)

1. **ANAYASA.md:** değişmeyen kurallar ayrı dosyada; PLAN.md esnek, ANAYASA sabit.
2. **İzin ayarı** (`.claude/settings.local.json`): Claude korunan dosyaları düzenleyemez, `main`'e push edemez.
3. **Otomatik kontrol** (`.github/workflows/asama2-koruma.yml`): her push'ta korunan dosya değiştiyse GitHub'da kırmızı ✖.
4. **İnceleme:** `main`'e birleştirme proje sahibinin onayıyla; proje sahibi kendi Claude'una "asama-2 dalını incele" diyerek değişikliklerin özetini alır.

Not: 2. katman Claude'un dosya düzenleme araçlarını engeller; kabuk komutlarıyla yapılan değişiklikleri 3. katman yakalar. Hiçbir katman tek başına mutlak değildir; birlikte sessiz değişikliği imkânsıza yakın hale getirirler.

## Sınırlar

Bu aşamada **gerçek emir yok**, işlem yetkili API anahtarı yok. Backtest ve kâğıt üzerinde işlem sonraki adımlardır.

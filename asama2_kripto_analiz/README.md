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
2. Claude Code'a şunu yaz:
   *"asama2_kripto_analiz/PLAN.md ve asama2_kripto_analiz/CLAUDE.md dosyalarını oku, Adım 0'dan başla."*
3. Claude her adımın sonunda kanıtıyla (test çıktısı, grafik resmi) rapor verir. İlk iş (Adım 0) eğitmenin BTC grafiğindeki dönüş noktalarını **kod yazılmadan önce** onaylamandır: [beklenen/btc_1d_2021_2022.md](beklenen/btc_1d_2021_2022.md).

## Dosyalar

- [PLAN.md](PLAN.md): amaç, sınırlar, güven protokolü, adımlar ve kabul kriterleri, "olmazsa" alternatifleri
- [CLAUDE.md](CLAUDE.md): Claude'un bu klasörde uyacağı kurallar
- [beklenen/](beklenen/): kabul testinin doğru cevapları (koddan önce dondurulur)

## Sınırlar

Bu aşamada **gerçek emir yok**, işlem yetkili API anahtarı yok. Backtest ve kâğıt üzerinde işlem sonraki adımlardır.

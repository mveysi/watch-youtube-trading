# Aşama 2: Claude Çalışma Kuralları

Bu klasör projenin **Aşama 2**'sidir: YouTube derslerinden öğrenilen kuralları (Aşama 1'in çıktısı `docs/wiki/Playbook.md`) mum verisi üzerinde Python ile hesaplayan analiz motoru. Plan: [PLAN.md](PLAN.md).

## Kesin kurallar

0. **[ANAYASA.md](ANAYASA.md) her şeyin üstündedir.** Sınırlar, güven protokolü ve korunan dosyalar orada. O dosyayı ve koruma düzeneğini (`koruma_kontrol.py`, `.github/`, `.claude/settings*.json`, `.claude/hooks/`) değiştirme; bir şey ANAYASA ile çelişiyorsa dur ve kullanıcıya sor.

1. **Sadece bu klasörde çalış.** Aşama 1'in dosyalarını (`watch_youtube/`, `.claude/skills/`, `docs/wiki_template/`, kök `README.md`, kök `CLAUDE.md`, `setup.py`) değiştirme. `docs/wiki/Playbook.md` sadece **okunur**.
2. **`asama-2` git dalında çalış.** `main`'e birleştirme ve push için kullanıcıdan onay al.
3. **Emir yok, işlem yetkili anahtar yok.** Sadece halka açık piyasa verisi okunur.
4. **Kural kaynağı Playbook'tur.** Kodladığın her kural, kullanıcının kendi `docs/wiki/Playbook.md` dosyasındaki bir ID'ye dayanır ve çıktıda o ID görünür. Playbook'ta olmayan kural uydurulmaz. Sayısı verilmemiş eşikler ayar olur (PLAN.md Adım 2), koda gömülmez.
5. **Güven protokolü (PLAN.md §5):** beklenen cevaplar koddan önce dondurulur ve sonradan değiştirilmez; her kabul testi bir grafik resmi üretir; tutmayan noktalar açıkça raporlanır; tek grafiğe göre ezber ayar yapılmaz.
6. **Adım adım ilerle.** Her adımın kabul kriteri sağlanmadan sonrakine geçme. Bir yöntem tutmazsa PLAN.md'deki "Olmazsa" alternatifini dene; o da tutmazsa ne denediğini yazıp kullanıcıya sor. Kabul kriterini gevşetme.
7. **Plan bir tahmindir, güncellenebilir** (PLAN.md §8): yöntem değişikliği serbest (bildir), kapsam/kabul kriteri değişikliği kullanıcı onayıyla, dondurulmuş beklenen cevaplar ve sınırlar değiştirilemez. Her değişikliği PLAN.md → Plan Değişiklik Günlüğü'ne yaz.
8. **Devam notu:** her adım sonunda ve her kullanıcı kararından sonra `DEVAM.md`'yi güncelle ve commit'le (compact/yeni oturum sonrası otomatik okunur). Push'tan önce `python asama2_kripto_analiz/koruma_kontrol.py` çalıştır; ✖ varsa push etme, kullanıcıya bildir.
9. **Her adım sonunda kısa rapor ver:** ne yapıldı, kabul kriteri sağlandı mı (kanıtıyla: test çıktısı, grafik dosyası), açık kalanlar.

## Teknik

- Python 3.11+, Aşama 1 ile aynı `.venv` kullanılabilir; Aşama 2'nin bağımlılıkları `asama2_kripto_analiz/requirements.txt` içinde ayrı tutulur.
- Zamanlar UTC; günlük mum = UTC 00:00 açılışlı.
- Çıktılar ve veri önbelleği `asama2_kripto_analiz/ciktilar/` altında (GitHub'a yüklenmez).
- Testler: `python -m pytest asama2_kripto_analiz/tests`.

# Aşama 2 Anayasası (değiştirilemez çekirdek)

> Bu dosya Aşama 2'nin **değişmeyen** kurallarını tutar. PLAN.md esnektir ve güncellenebilir; bu dosya değildir.
> - Claude bu dosyayı **düzenleyemez** (`kurulum/settings.local.json.ornek` ile teknik olarak engellenir).
> - `asama-2` dalında bu dosyada yapılan her değişiklik GitHub'daki otomatik kontrolde **kırmızı ✖** verir.
> - Değişmesi gerekirse bunu sadece proje sahibi, `main` dalında, bilerek yapar.

## A. Sınırlar

1. **Gerçek emir yok.** Borsaya emir gönderen, bakiye okuyan veya işlem yetkili API anahtarı kullanan kod yazılmaz. Sadece halka açık (anahtarsız) piyasa verisi okunur.
2. **Aşama 1'e dokunulmaz.** `asama2_kripto_analiz/` dışındaki hiçbir dosya `asama-2` dalında değiştirilmez. `docs/wiki/Playbook.md` sadece **okunur**.
3. **Ayrı dal.** Çalışma `asama-2` dalında yapılır. `main`'e birleştirme yalnızca proje sahibinin onayıyla olur.
4. **Kural kaynağı Playbook'tur.** Playbook'ta olmayan bir işlem kuralı koda eklenmez. Eğitmenin sayı vermediği eşikler ayar olur, uydurulmaz.

## B. Güven protokolü

1. **Doğru cevap koddan önce dondurulur.** `beklenen/` dosyaları eğitmenin işaretlemelerinden çıkarılır, kullanıcı onaylar ve **`main`'e alınarak dondurulur**. Dondurulmuş bir dosya `asama-2` dalında değiştirilirse otomatik kontrol kırmızı verir.
2. **Görsel kanıt.** Her kabul testi, eğitmenin ekran görüntüsüyle yan yana karşılaştırılabilecek etiketli bir grafik resmi üretir.
3. **Uyuşmazlık saklanmaz.** Her beklenen nokta "tuttu / tutmadı / kısmen" diye raporlanır. Tutmayanların nedeni yazılır.
4. **Ezber yasak.** Ayarlar tek bir grafiğe göre aşırı ayarlanmaz; başka bir örnekte de denenir ve ayrıca raporlanır.
5. **Bağımsız tekrar.** Aynı komut başka bir bilgisayarda aynı olayları vermelidir.

## C. Plan değişikliklerinde yasaklar

1. Dondurulmuş `beklenen/` dosyalarını kod sonucuna uydurmak.
2. Bu dosyadaki sınırları veya güven protokolünü kaldırmak, gevşetmek ya da "plan böyle diyor" diyerek aşmak.
3. Kabul kriterini kullanıcının açık onayı olmadan gevşetmek.
4. Koruma düzeneğini (`koruma_kontrol.py`, `.github/workflows/asama2-koruma.yml`, `.claude/settings*.json`, bu dosya) değiştirmek veya devre dışı bırakmak.

## D. Korunan dosyalar (otomatik kontrolün baktıkları)

| Dosya / klasör | Kural |
|---|---|
| `asama2_kripto_analiz/` dışındaki her şey | `asama-2` dalında değişemez |
| `asama2_kripto_analiz/ANAYASA.md` | değişemez |
| `asama2_kripto_analiz/koruma_kontrol.py` | değişemez |
| `asama2_kripto_analiz/beklenen/*` | `main`'deki sürümünde "ONAYLANDI" yazıyorsa değişemez |

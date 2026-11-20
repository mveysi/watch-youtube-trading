**Özet:** Sistemin ders ders nasıl öğrendiğinin günlüğü. Her işlenen ders bir kayıt ekler: ne yeni öğrenildi, ne inceltildi/düzeltildi, hangi sorular kapandı/açıldı ve ders sonrası bilgi durumu.
**Kütüphaneler/Teknolojiler:** Öğrenme günlüğü, Playbook
**Bağlantılar:** [[Playbook]], [[Videos]], [[Index]]
**Kaynak Video:** Her kaydın kendi videosu başlığında yazılır.

> **Kurallar:** Bu dosyaya **sadece sona ekleme** yapılır; eski kayıtlar değiştirilmez. Yeni ders işlerken bu dosyanın tamamı **okunmaz**; gerekirse yalnızca son kayıt okunur: `playbook-check --last-log`.
> Güncel bilgi her zaman [[Playbook]] ve konu sayfalarındadır; burası "nasıl buraya geldik" kaydıdır.

Kayıt formatı (başlık satırı biçimi önemlidir, `playbook-check` video ID'yi parantezden okur):

```markdown
## Ders N: <kısa başlık> (VIDEO_ID)
- **Tarih:** YYYY-MM-DD · **Transcript:** whisper | vtt (YouTube'dan doldurulan bölüm: N)
- **Ders öncesi aranan:** Q-0xx, Q-0yy (bu dersin konusuyla ilgili açık/beklenen sorular)
- **Yeni öğrenilen:** OB-003 (açık kural), ENT-007 (türetilmiş) … · yeni kavram: [[Sayfa]]
- **İnceltilen / düzeltilen:** MS-004 (tanım daraldı: …) · etkilenen sayfalar: [[MarketStructure]] …
- **Kapanan sorular:** Q-020 → "…" (12:40)
- **Yeni sorular:** Q-027 (açık) · Q-028 (beklenen: Likidite dersi)
- **Çelişkiler:** yok | <kısa> → karar: … / kullanıcı kararı bekleniyor
- **Belirsiz kalan:** "hacimli mum" (ölçü yok) …
- **Bilgi durumu:** aktif kural X (koda hazır Y) · açık soru Z · beklenen W · bekleyen çelişki V
```

---

<!-- Kayıtlar bu satırın altına, en yenisi en altta olacak şekilde eklenir. -->

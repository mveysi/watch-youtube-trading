#!/usr/bin/env bash
# SessionStart hook: oturum açılışında, compact'tan ve resume'dan sonra devam notlarını
# Claude'un bağlamına koyar (stdout → bağlam). Böylece compact'ta kaybolan ayrıntılar
# Claude'un hatırlamasına bağlı kalmadan geri gelir.
# Okunan dosyalar (hangisi varsa):
#   docs/wiki/DEVAM.md               Aşama 1 (ders işleme) devam notu — kişiye özel, GitHub'a gitmez
#   asama2_kripto_analiz/DEVAM.md    Aşama 2 (analiz motoru) devam notu — asama-2 dalında
#   OTURUM_NOTLARI.md                proje sahibinin yerel notu (sadece "DEVAM NOKTASI" bölümü)

kok="${CLAUDE_PROJECT_DIR:-.}"
cd "$kok" 2>/dev/null || exit 0

goster() {  # $1 = dosya, $2 = başlık
  [ -f "$1" ] || return 0
  printf '\n===== %s (%s) =====\n' "$2" "$1"
  head -n 100 "$1"
  printf '\n'
}

printf 'DEVAM NOTLARI (otomatik). Önce bunları oku; işe devam etmeden önce güncel durumu bunlara göre belirle.\n'
goster "docs/wiki/DEVAM.md" "Aşama 1 devam notu"
goster "asama2_kripto_analiz/DEVAM.md" "Aşama 2 devam notu"
if [ -f "OTURUM_NOTLARI.md" ]; then
  printf '\n===== Proje sahibi notu: DEVAM NOKTASI (OTURUM_NOTLARI.md) =====\n'
  sed -n '/DEVAM NOKTASI/,/^## 1\./p' OTURUM_NOTLARI.md | head -n 100
  printf '\n'
fi
exit 0

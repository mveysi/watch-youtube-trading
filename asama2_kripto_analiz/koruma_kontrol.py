"""Aşama 2 koruma kontrolü.

`asama-2` dalının `main`'e göre neyi değiştirdiğine bakar ve ANAYASA.md §D'deki
korunan dosyalardan biri değiştiyse hata verir (çıkış kodu 1).

Kullanım (repo kökünden):
    python asama2_kripto_analiz/koruma_kontrol.py                 # main'e göre
    python asama2_kripto_analiz/koruma_kontrol.py --base origin/main

GitHub'da `.github/workflows/asama2-koruma.yml` her push'ta bunu çalıştırır.
Sadece Python standart kütüphanesi kullanır.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

KLASOR = "asama2_kripto_analiz/"
HEP_KORUNAN = {
    KLASOR + "ANAYASA.md",
    KLASOR + "koruma_kontrol.py",
}
BEKLENEN = KLASOR + "beklenen/"
DONDURMA_ISARETI = "ONAYLANDI"


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} başarısız: {out.stderr.strip()}")
    return out.stdout


def dosya_main_de(base: str, yol: str) -> str | None:
    try:
        return git("show", f"{base}:{yol}")
    except RuntimeError:
        return None  # main'de yok (yeni dosya)


def kontrol(base: str) -> list[str]:
    ortak = git("merge-base", base, "HEAD").strip()
    degisen = [s for s in git("diff", "--name-only", f"{ortak}..HEAD").splitlines() if s]
    # Henüz commit'lenmemiş değişiklikleri de say (yerel kullanım için)
    degisen += [s for s in git("diff", "--name-only", "HEAD").splitlines() if s]
    degisen = sorted(set(degisen))

    hatalar = []
    for yol in degisen:
        if not yol.startswith(KLASOR):
            hatalar.append(f"Aşama 2 klasörü dışında değişiklik: {yol}  (ANAYASA §A.2)")
        elif yol in HEP_KORUNAN:
            hatalar.append(f"Korunan dosya değişmiş: {yol}  (ANAYASA §D)")
        elif yol.startswith(BEKLENEN):
            main_surumu = dosya_main_de(base, yol)
            if main_surumu is not None and DONDURMA_ISARETI in main_surumu:
                hatalar.append(f"Dondurulmuş beklenen dosyası değişmiş: {yol}  (ANAYASA §B.1)")
    return hatalar


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Aşama 2 koruma kontrolü")
    p.add_argument("--base", default="main", help="Karşılaştırılacak dal (varsayılan: main)")
    a = p.parse_args()
    try:
        hatalar = kontrol(a.base)
    except RuntimeError as e:
        print(f"✖ Kontrol çalışamadı: {e}")
        return 2
    if hatalar:
        print(f"✖ KORUMA İHLALİ ({len(hatalar)}):")
        for h in hatalar:
            print(f"  - {h}")
        print("\nBu değişiklikler main'e alınmamalı. Proje sahibine danışın (ANAYASA.md).")
        return 1
    print(f"✔ Koruma kontrolü temiz ({a.base} ile karşılaştırıldı).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

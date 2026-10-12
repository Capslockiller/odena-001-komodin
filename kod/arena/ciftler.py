# yazan: codex · gpt-6.1-sol
"""Kör hücre kimliklerinden tekrara eşlenmiş model çiftleri kurar."""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path

ETIKET = re.compile(r"^(.+)-([^-]+)-r(\d+)$")


def etiketi_ayir(etiket: str) -> tuple[str, str, int]:
    eslesme = ETIKET.match(etiket)
    if not eslesme:
        raise ValueError(f"etiket model-kart-rN biçiminde değil: {etiket}")
    return eslesme.group(1), eslesme.group(2), int(eslesme.group(3))


def hucreleri_haritadan(harita: dict[str, str]) -> list[dict]:
    sonuc = []
    for kimlik, etiket in sorted(harita.items()):
        model, kart, tekrar = etiketi_ayir(etiket)
        sonuc.append({"kimlik": kimlik, "etiket": etiket, "model": model, "kart": kart, "tekrar": tekrar})
    return sonuc


def ciftleri_uret(hucreler: list[dict], tohum: int) -> list[dict[str, str]]:
    """Her model çifti × ortak tekrar için tek, yönü tohumlu çift üretir."""
    rng = random.Random(tohum)
    dizin: dict[str, dict[int, dict]] = defaultdict(dict)
    for hucre in hucreler:
        model = str(hucre.get("model") or etiketi_ayir(str(hucre["etiket"]))[0])
        tekrar = int(hucre.get("tekrar") or etiketi_ayir(str(hucre["etiket"]))[2])
        if tekrar in dizin[model]:
            raise ValueError(f"aynı model/tekrar birden çok kez var: {model} r{tekrar}")
        dizin[model][tekrar] = hucre
    taslak = []
    modeller = sorted(dizin)
    for i, a in enumerate(modeller):
        for b in modeller[i + 1 :]:
            for tekrar in sorted(set(dizin[a]) & set(dizin[b])):
                sol, sag = dizin[a][tekrar], dizin[b][tekrar]
                if rng.randrange(2):
                    sol, sag = sag, sol
                taslak.append({"sol": str(sol["kimlik"]), "sag": str(sag["kimlik"])})
    rng.shuffle(taslak)
    return [dict(cift_id=f"c{sira:05d}", **cift) for sira, cift in enumerate(taslak, 1)]


def insan_alt_kumesi(ciftler: list[dict], hucreler: list[dict], m: int, tohum: int) -> list[dict]:
    """Her model çifti için tam m kayıt seçer; değerlendirici tohumu ayrıdır."""
    if m < 1:
        raise ValueError("m en az 1 olmalı")
    model = {str(h["kimlik"]): str(h.get("model") or etiketi_ayir(str(h["etiket"]))[0]) for h in hucreler}
    gruplar: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for cift in ciftler:
        gruplar[tuple(sorted((model[cift["sol"]], model[cift["sag"]])))].append(cift)
    rng = random.Random(tohum)
    secilen = []
    for anahtar in sorted(gruplar):
        aday = list(gruplar[anahtar])
        if len(aday) < m:
            raise ValueError(f"{anahtar} için {m} kayıt yok (var={len(aday)})")
        secilen.extend(rng.sample(aday, m))
    rng.shuffle(secilen)
    return [dict(cift) for cift in secilen]


def _yaz(yol: str | Path, veri: object) -> None:
    Path(yol).write_text(json.dumps(veri, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--harita", required=True)
    ap.add_argument("--cikis", required=True)
    ap.add_argument("--tohum", type=int, required=True)
    ap.add_argument("--insan-cikis")
    ap.add_argument("--insan-m", type=int, default=1)
    ap.add_argument("--degerlendirici-tohumu", type=int)
    a = ap.parse_args()
    belge = json.loads(Path(a.harita).read_text(encoding="utf-8"))
    hucreler = hucreleri_haritadan(belge["harita"])
    ciftler = ciftleri_uret(hucreler, a.tohum)
    _yaz(a.cikis, {"surum": 1, "tohum": a.tohum, "ciftler": ciftler})
    insan_sayisi = 0
    if a.insan_cikis:
        if a.degerlendirici_tohumu is None:
            ap.error("--insan-cikis için --degerlendirici-tohumu gerekli")
        secim = insan_alt_kumesi(ciftler, hucreler, a.insan_m, a.degerlendirici_tohumu)
        _yaz(a.insan_cikis, {"surum": 1, "m": a.insan_m, "ciftler": secim})
        insan_sayisi = len(secim)
    print(f"CIFTLER_OK cift={len(ciftler)} insan={insan_sayisi} cikis={a.cikis}")


if __name__ == "__main__":
    main()

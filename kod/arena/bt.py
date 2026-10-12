# yazan: codex · gpt-6.1-sol
"""Saf Python Bradley-Terry uyumu, Elo ölçeği ve bootstrap aralıkları."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Iterable

Oy = tuple[str, str, float]


def uydur(
    oylar: Iterable[Oy],
    modeller: Iterable[str] | None = None,
    *,
    oncul: float = 1e-3,
    azami_adim: int = 10_000,
    tolerans: float = 1e-11,
) -> dict[str, dict[str, float]]:
    """Bradley-Terry MM ile güçleri uydurup ortalaması 1000 olan Elo döndürür.

    Her model çifti yön başına ``oncul`` kadar simetrik sanal galibiyet alır.
    Bu küçük öncül, sıfır galibiyetli ve ayrık çizgeli veride sonsuz/0 güçleri
    önler; taraflardan hiçbirini kayırmaz.
    """
    oylar = list(oylar)
    adlar = sorted(set(modeller or ()) | {ad for a, b, _ in oylar for ad in (a, b)})
    if not adlar:
        return {}
    if len(adlar) == 1:
        return {adlar[0]: {"guc": 1.0, "elo": 1000.0}}
    if oncul <= 0:
        raise ValueError("oncul pozitif olmalı")

    galibiyet = {ad: oncul * (len(adlar) - 1) for ad in adlar}
    karsilasma: dict[tuple[str, str], float] = {
        (a, b): 2.0 * oncul
        for i, a in enumerate(adlar)
        for b in adlar[i + 1 :]
    }
    for a, b, sonuc in oylar:
        if a == b or sonuc not in (0, 0.0, 0.5, 1, 1.0):
            raise ValueError(f"geçersiz oy: {(a, b, sonuc)!r}")
        anahtar = tuple(sorted((a, b)))
        karsilasma[anahtar] += 1.0
        galibiyet[a] += float(sonuc)
        galibiyet[b] += 1.0 - float(sonuc)

    guc = {ad: 1.0 for ad in adlar}
    for _ in range(azami_adim):
        yeni = {}
        for ad in adlar:
            payda = 0.0
            for oteki in adlar:
                if oteki == ad:
                    continue
                n = karsilasma[tuple(sorted((ad, oteki)))]
                payda += n / (guc[ad] + guc[oteki])
            yeni[ad] = galibiyet[ad] / payda
        geo = math.exp(sum(math.log(max(x, 1e-300)) for x in yeni.values()) / len(yeni))
        yeni = {ad: x / geo for ad, x in yeni.items()}
        fark = max(abs(math.log(yeni[ad] / guc[ad])) for ad in adlar)
        guc = yeni
        if fark < tolerans:
            break

    ham_elo = {ad: 400.0 * math.log10(guc[ad]) for ad in adlar}
    merkez = sum(ham_elo.values()) / len(ham_elo)
    return {
        ad: {"guc": guc[ad], "elo": 1000.0 + ham_elo[ad] - merkez}
        for ad in adlar
    }


def bootstrap(
    oylar: Iterable[Oy],
    modeller: Iterable[str] | None = None,
    *,
    ornek_sayisi: int = 1000,
    tohum: int = 1,
    oncul: float = 1e-3,
) -> dict[str, dict[str, float | int | list[float]]]:
    """Oyları yeniden örnekleyip yüzde 95 güven aralığı ve katman üretir."""
    oylar = list(oylar)
    adlar = sorted(set(modeller or ()) | {ad for a, b, _ in oylar for ad in (a, b)})
    ana = uydur(oylar, adlar, oncul=oncul)
    if not ana:
        return {}
    if ornek_sayisi < 1:
        raise ValueError("ornek_sayisi en az 1 olmalı")
    rng = random.Random(tohum)
    dagilim = defaultdict(list)
    for _ in range(ornek_sayisi):
        secim = [oylar[rng.randrange(len(oylar))] for _ in oylar] if oylar else []
        uyum = uydur(secim, adlar, oncul=oncul)
        for ad in adlar:
            dagilim[ad].append(uyum[ad]["elo"])
    sonuc: dict[str, dict[str, float | int | list[float]]] = {}
    for ad in adlar:
        xs = sorted(dagilim[ad])
        lo = xs[int((len(xs) - 1) * 0.025)]
        hi = xs[int((len(xs) - 1) * 0.975)]
        sonuc[ad] = {**ana[ad], "ga95": [lo, hi]}
    katmanlari_ata(sonuc)
    return sonuc


def katmanlari_ata(sonuc: dict[str, dict[str, float | int | list[float]]]) -> None:
    """Liderle GA'sı kesişenleri aynı katmana alıp kalanlarda yineler."""
    kalan = sorted(sonuc, key=lambda ad: float(sonuc[ad]["elo"]), reverse=True)
    katman = 1
    while kalan:
        lider = kalan[0]
        llo, lhi = sonuc[lider]["ga95"]  # type: ignore[misc]
        grup = []
        for ad in kalan:
            lo, hi = sonuc[ad]["ga95"]  # type: ignore[misc]
            if float(lo) <= float(lhi) and float(hi) >= float(llo):
                grup.append(ad)
        for ad in grup:
            sonuc[ad]["katman"] = katman
            kalan.remove(ad)
        katman += 1

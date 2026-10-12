# yazan: codex · gpt-6.1-sol
"""İnsan/yapay oylarından lig, ölçüt geçerliği ve değerlendirici uyumu üretir."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .bt import bootstrap
from .ciftler import etiketi_ayir


def ortalama_siralar(degerler: list[float]) -> list[float]:
    """Küçükten büyüğe, bağlarda ortalama sıra (1 tabanlı)."""
    sirali = sorted(range(len(degerler)), key=degerler.__getitem__)
    sonuc = [0.0] * len(degerler)
    i = 0
    while i < len(sirali):
        j = i + 1
        while j < len(sirali) and degerler[sirali[j]] == degerler[sirali[i]]:
            j += 1
        sira = ((i + 1) + j) / 2.0
        for k in sirali[i:j]:
            sonuc[k] = sira
        i = j
    return sonuc


def spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    rx, ry = ortalama_siralar(x), ortalama_siralar(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    pay = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return pay / (sx * sy) if sx and sy else None


def krippendorff_nominal(maddeler: dict[str, list[str]]) -> float | None:
    """Eksik puanlara izin veren nominal Krippendorff alfa."""
    kullanilan = [oylar for oylar in maddeler.values() if len(oylar) >= 2]
    if not kullanilan:
        return None
    gozlenen_uyusmazlik = 0.0
    toplam_eslesme = 0
    toplamlar: dict[str, int] = defaultdict(int)
    for oylar in kullanilan:
        n = len(oylar)
        gozlenen_uyusmazlik += sum(a != b for a in oylar for b in oylar) / (n - 1)
        toplam_eslesme += n
        for oy in oylar:
            toplamlar[oy] += 1
    toplam = sum(toplamlar.values())
    if toplam < 2:
        return None
    do = gozlenen_uyusmazlik / toplam_eslesme
    de = 1.0 - sum(n * (n - 1) for n in toplamlar.values()) / (toplam * (toplam - 1))
    return 1.0 - do / de if de else (1.0 if do == 0 else None)


def uyum_ozeti(kayitlar: list[dict]) -> dict:
    """Aynı maddede farklı değerlendiricilerin yüzde uyumu ve alfası."""
    maddeler: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for kayit in kayitlar:
        maddeler[str(kayit["cift_id"])].append((str(kayit["degerlendirici"]), str(kayit["karar"])))
    oy_maddeleri = {}
    ayni = toplam = 0
    for cift_id, degerler in maddeler.items():
        son: dict[str, str] = {}
        for degerlendirici, karar in degerler:
            son[degerlendirici] = karar
        if len(son) < 2:
            continue
        oylar = list(son.values())
        oy_maddeleri[cift_id] = oylar
        for i, a in enumerate(oylar):
            for b in oylar[i + 1 :]:
                toplam += 1
                ayni += a == b
    return {
        "ortak_cift": len(oy_maddeleri),
        "yuzde_uyum": 100.0 * ayni / toplam if toplam else None,
        "krippendorff_alpha": krippendorff_nominal(oy_maddeleri),
    }


def gruplar_arasi_uyum(insan: list[dict], yapay: list[dict]) -> dict:
    i_dizin: dict[str, list[str]] = defaultdict(list)
    y_dizin: dict[str, list[str]] = defaultdict(list)
    for k in insan:
        i_dizin[str(k["cift_id"])].append(str(k["karar"]))
    for k in yapay:
        y_dizin[str(k["cift_id"])].append(str(k["karar"]))
    ortak = sorted(set(i_dizin) & set(y_dizin))
    ayni = toplam = 0
    maddeler = {}
    for cift in ortak:
        for a in i_dizin[cift]:
            for b in y_dizin[cift]:
                toplam += 1
                ayni += a == b
        maddeler[cift] = i_dizin[cift] + y_dizin[cift]
    return {
        "ortak_cift": len(ortak),
        "yuzde_uyum": 100.0 * ayni / toplam if toplam else None,
        "birlesik_krippendorff_alpha": krippendorff_nominal(maddeler),
    }


def metrikleri_oku(olcum: str | Path) -> dict[str, dict[str, float]]:
    """Tüm sayısal yaprakları ve dört kanonik ölçütü model medyanına indirger."""
    birikim: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for yol in sorted(Path(olcum).glob("*/hucre.json")):
        hucre = json.loads(yol.read_text(encoding="utf-8"))
        if hucre.get("durum") == "KIRMIZI":
            continue
        if str(hucre.get("etiket") or yol.parent.name) == "usta":  # referans hücresi, yarışmacı değil
            continue
        model = etiketi_ayir(str(hucre.get("etiket") or yol.parent.name))[0]
        duz: dict[str, float] = {}
        _sayisal_yapraklar(hucre, "", duz)
        sekil = hucre.get("sekil_mesafesi") or {}
        yonler = [sekil.get(ad, {}).get("ortalama") for ad in ("biz->usta", "usta->biz")]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in yonler):
            duz["sekil_ortalama"] = statistics.mean(yonler)
        gorsel = hucre.get("gorsel") or {}
        for kaynak, ad in (("siglip2", "siglip2_best"), ("dinov2", "dinov2_best")):
            deger = (gorsel.get(kaynak) or {}).get("best")
            if isinstance(deger, (int, float)) and not isinstance(deger, bool):
                duz[ad] = float(deger)
        if isinstance(hucre.get("kontrol_kirmizi"), (int, float)):
            duz["kontrol_kirmizi"] = float(hucre["kontrol_kirmizi"])
        vertex = hucre.get("tel_vertex", (hucre.get("istatistik") or {}).get("ham_v"))
        if isinstance(vertex, (int, float)) and not isinstance(vertex, bool):
            duz["kafes_vertex"] = float(vertex)
        for ad, deger in duz.items():
            birikim[ad][model].append(deger)
    return {
        ad: {model: statistics.median(xs) for model, xs in modeller.items()}
        for ad, modeller in sorted(birikim.items())
    }


def _sayisal_yapraklar(nesne: object, onek: str, cikti: dict[str, float]) -> None:
    if isinstance(nesne, dict):
        for ad, deger in nesne.items():
            yol = f"{onek}.{ad}" if onek else str(ad)
            _sayisal_yapraklar(deger, yol, cikti)
    elif isinstance(nesne, (int, float)) and not isinstance(nesne, bool):
        cikti[onek] = float(nesne)


def ligi_olustur(
    olcum: str | Path,
    harita: dict[str, str],
    ciftler: list[dict],
    insan_kayitlari: list[dict],
    yapay_kayitlari: list[dict],
    cikis: str | Path,
    *,
    tohum: int = 1,
    bootstrap_sayisi: int = 1000,
) -> dict:
    cift_dizini = {str(c["cift_id"]): c for c in ciftler}
    modeller = sorted({etiketi_ayir(etiket)[0] for etiket in harita.values()})
    insan_gecerli = _gecerli_kayitlar(insan_kayitlari, "degerlendirici")
    yapay_gecerli = _gecerli_kayitlar(yapay_kayitlari, "hakem")
    insan_oy = _bt_oylari(insan_gecerli, cift_dizini, harita)
    yapay_oy = _bt_oylari(yapay_gecerli, cift_dizini, harita)
    tablolar = {
        "insan": bootstrap(insan_oy, modeller, ornek_sayisi=bootstrap_sayisi, tohum=tohum) if insan_oy else {},
        "yapay": bootstrap(yapay_oy, modeller, ornek_sayisi=bootstrap_sayisi, tohum=tohum + 1) if yapay_oy else {},
    }
    metrikler = metrikleri_oku(olcum)
    gecerlilik = {}
    if tablolar["insan"]:
        elo = {ad: float(veri["elo"]) for ad, veri in tablolar["insan"].items()}
        for ad, degerler in metrikler.items():
            ortak = sorted(set(elo) & set(degerler))
            gecerlilik[ad] = {"n": len(ortak), "spearman": spearman(
                [degerler[m] for m in ortak], [elo[m] for m in ortak]
            )}
    insan_uyum_girdi = [{"cift_id": k["cift_id"], "degerlendirici": k["degerlendirici"], "karar": k["karar"]}
                         for k in insan_gecerli]
    yapay_uyum_girdi = [{"cift_id": k["cift_id"], "karar": k["karar"]} for k in yapay_gecerli]
    belge = {
        "surum": 1,
        "bootstrap_sayisi": bootstrap_sayisi,
        "tablolar": tablolar,
        "metrik_medyanlari": metrikler,
        "insan_elo_spearman": gecerlilik,
        "insan_degerlendirici_uyumu": uyum_ozeti(insan_uyum_girdi),
        "yapay_insan_uyumu": gruplar_arasi_uyum(insan_uyum_girdi, yapay_uyum_girdi),
    }
    cikis = Path(cikis)
    cikis.mkdir(parents=True, exist_ok=True)
    (cikis / "lig.json").write_text(json.dumps(belge, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (cikis / "LIG.md").write_text(_markdown(belge), encoding="utf-8", newline="\n")
    return belge


def _gecerli_kayitlar(kayitlar: Iterable[dict], degerlendirici_alani: str) -> list[dict]:
    sonuc = []
    for kayit in kayitlar:
        if kayit.get("durum") not in (None, "sayildi") or kayit.get("karar") not in {"SOL", "SAG", "BERABERE"}:
            continue
        if degerlendirici_alani not in kayit:
            continue
        sonuc.append(kayit)
    return sonuc


def _bt_oylari(kayitlar: list[dict], ciftler: dict[str, dict], harita: dict[str, str]) -> list[tuple[str, str, float]]:
    sonuc = []
    for kayit in kayitlar:
        cift = ciftler[str(kayit["cift_id"])]
        a = etiketi_ayir(harita[str(cift["sol"])])[0]
        b = etiketi_ayir(harita[str(cift["sag"])])[0]
        puan = {"SOL": 1.0, "SAG": 0.0, "BERABERE": 0.5}[kayit["karar"]]
        sonuc.append((a, b, puan))
    return sonuc


def _markdown(belge: dict) -> str:
    satirlar = ["# Arena ligi", "", f"Bootstrap: {belge['bootstrap_sayisi']} örnek.", ""]
    for tur, baslik in (("insan", "İnsan ligi"), ("yapay", "Yapay hakem ligi")):
        satirlar += [f"## {baslik}", "", "| Model | Elo | %95 GA | Katman |", "|---|---:|---:|---:|"]
        tablo = belge["tablolar"][tur]
        for model in sorted(tablo, key=lambda m: tablo[m]["elo"], reverse=True):
            v = tablo[model]
            satirlar.append(f"| {model} | {v['elo']:.1f} | {v['ga95'][0]:.1f}–{v['ga95'][1]:.1f} | {v['katman']} |")
        if not tablo:
            satirlar.append("| — | — | — | — |")
        satirlar.append("")
    satirlar += ["## Sayısal ölçütlerin insan Elo geçerliği", "", "| Ölçüt | n | Spearman ρ |", "|---|---:|---:|"]
    for ad, v in belge["insan_elo_spearman"].items():
        rho = "—" if v["spearman"] is None else f"{v['spearman']:.4f}"
        satirlar.append(f"| {ad} | {v['n']} | {rho} |")
    satirlar += ["", "## Uyum", "", "```json", json.dumps({
        "insan": belge["insan_degerlendirici_uyumu"],
        "yapay_insan": belge["yapay_insan_uyumu"],
    }, ensure_ascii=False, indent=2), "```", ""]
    return "\n".join(satirlar)


def _json_oku(yol: str) -> object:
    return json.loads(Path(yol).read_text(encoding="utf-8"))


def _jsonl_oku(yollar: list[str]) -> list[dict]:
    sonuc = []
    for yol in yollar:
        sonuc.extend(json.loads(s) for s in Path(yol).read_text(encoding="utf-8").splitlines() if s.strip())
    return sonuc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--olcum", required=True)
    ap.add_argument("--harita", required=True)
    ap.add_argument("--ciftler", required=True)
    ap.add_argument("--insan-oy", action="append", default=[])
    ap.add_argument("--yapay-oy", action="append", default=[])
    ap.add_argument("--cikis", required=True)
    ap.add_argument("--tohum", type=int, default=1)
    a = ap.parse_args()
    belge = ligi_olustur(
        a.olcum, _json_oku(a.harita)["harita"], _json_oku(a.ciftler)["ciftler"],
        _jsonl_oku(a.insan_oy), _jsonl_oku(a.yapay_oy), a.cikis, tohum=a.tohum,
    )
    print(f"LIG_OK insan={len(belge['tablolar']['insan'])} yapay={len(belge['tablolar']['yapay'])} cikis={a.cikis}")


if __name__ == "__main__":
    main()

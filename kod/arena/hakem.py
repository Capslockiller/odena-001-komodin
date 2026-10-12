# yazan: codex · gpt-6.1-sol
"""İki sunum sırasıyla, aile sızıntısını engelleyen yapay hakem koşucusu."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from .ciftler import etiketi_ayir

Yurutucu = Callable[[str, str, str, str], str]

AILELER = {
    "opus-med": "claude",
    "sonnet-med": "claude",
    "haiku": "claude",
    "fable-med": "claude",
    "sol-med": "openai",
    "astra-med": "openai",
    "gemini-high": "google",
    "gemini-pro": "google",
    "inkling": "thinkingmachines",
    "gemma": "google",
}
HAKEM_AILESI = {"gemini": "google", "sol": "openai"}

ISTEM = """Bir 3D sanatçısı olarak hangisini teslim alırdın?

İki kör paftayı yalnızca sol ve sağ olarak değerlendir. Tek bir seçenek ver:
SOL / SAĞ / BERABERE.

Yalnızca şu kesin JSON biçiminde yanıtla:
{"karar": "SOL|SAG|BERABERE", "gerekce": "kısa gerekçe"}
"""


def yaniti_coz(metin: str) -> dict | None:
    """Kod çitindeki/çevresindeki ilk geçerli karar JSON nesnesini çözer."""
    adaylar = [metin.strip()]
    adaylar.extend(re.findall(r"\{[^{}]*\}", metin, flags=re.DOTALL))
    for aday in adaylar:
        aday = re.sub(r"^```(?:json)?\s*|\s*```$", "", aday.strip(), flags=re.IGNORECASE)
        try:
            veri = json.loads(aday)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(veri, dict):
            continue
        karar = str(veri.get("karar", "")).strip().upper().replace("Ğ", "G")
        if karar in {"SOL", "SAG", "BERABERE"}:
            return {"karar": karar, "gerekce": str(veri.get("gerekce", ""))}
    return None


def hakemleri_kostur(
    ciftler: list[dict],
    harita: dict[str, str],
    pafta_klasoru: str | Path,
    sonuc_yolu: str | Path,
    hakemler: list[str],
    yurutucu: Yurutucu,
) -> dict[str, dict[str, int | float]]:
    """Eksik hakem/çift kayıtlarını çalıştırıp JSONL'ye ekler."""
    sonuc_yolu = Path(sonuc_yolu)
    sonuc_yolu.parent.mkdir(parents=True, exist_ok=True)
    onceki = _jsonl_oku(sonuc_yolu)
    tamam = {(str(k.get("hakem")), str(k.get("cift_id"))) for k in onceki}
    with sonuc_yolu.open("a", encoding="utf-8", newline="\n") as cikti:
        for hakem in hakemler:
            if hakem not in HAKEM_AILESI:
                raise ValueError(f"bilinmeyen hakem: {hakem}")
            for cift in ciftler:
                anahtar = (hakem, str(cift["cift_id"]))
                if anahtar in tamam:
                    continue
                sol_id, sag_id = str(cift["sol"]), str(cift["sag"])
                sol_model = etiketi_ayir(harita[sol_id])[0]
                sag_model = etiketi_ayir(harita[sag_id])[0]
                temel = {"surum": 1, "hakem": hakem, "cift_id": cift["cift_id"]}
                if HAKEM_AILESI[hakem] in {AILELER.get(sol_model), AILELER.get(sag_model)}:
                    kayit = {**temel, "durum": "cekimser", "karar": None, "ham": [], "cozum": []}
                else:
                    sol_png = str(Path(pafta_klasoru) / f"{sol_id}.png")
                    sag_png = str(Path(pafta_klasoru) / f"{sag_id}.png")
                    ham1 = yurutucu(hakem, sol_png, sag_png, ISTEM)
                    ham2 = yurutucu(hakem, sag_png, sol_png, ISTEM)
                    cozum1, cozum2 = yaniti_coz(ham1), yaniti_coz(ham2)
                    kayit = _iki_sirayi_birlestir(temel, ham1, ham2, cozum1, cozum2)
                cikti.write(json.dumps(kayit, ensure_ascii=False) + "\n")
                cikti.flush()
                onceki.append(kayit)
    return rapor_uret(onceki, hakemler)


def _iki_sirayi_birlestir(temel: dict, ham1: str, ham2: str, cozum1: dict | None, cozum2: dict | None) -> dict:
    ortak = {**temel, "ham": [ham1, ham2], "cozum": [cozum1, cozum2]}
    if cozum1 is None or cozum2 is None:
        return {**ortak, "durum": "gecersiz", "karar": None}
    ilk = cozum1["karar"]
    ikinci = {"SOL": "SAG", "SAG": "SOL", "BERABERE": "BERABERE"}[cozum2["karar"]]
    if ilk != ikinci:
        return {**ortak, "durum": "tutarsiz", "karar": None}
    return {**ortak, "durum": "sayildi", "karar": ilk}


def rapor_uret(kayitlar: list[dict], hakemler: list[str] | None = None) -> dict[str, dict[str, int | float]]:
    hakemler = hakemler or sorted({str(k["hakem"]) for k in kayitlar})
    rapor = {}
    for hakem in hakemler:
        bunlar = [k for k in kayitlar if k.get("hakem") == hakem]
        sayim = {ad: sum(k.get("durum") == durum for k in bunlar) for ad, durum in (
            ("counted", "sayildi"), ("tutarsiz", "tutarsiz"),
            ("gecersiz", "gecersiz"), ("cekimser", "cekimser"))}
        ham_kararlar = [c["karar"] for k in bunlar for c in k.get("cozum", []) if isinstance(c, dict)]
        sayim["position_bias_rate"] = (
            sum(x == "SOL" for x in ham_kararlar) / len(ham_kararlar) if ham_kararlar else 0.0
        )
        rapor[hakem] = sayim
    return rapor


def _jsonl_oku(yol: Path) -> list[dict]:
    if not yol.exists():
        return []
    return [json.loads(satir) for satir in yol.read_text(encoding="utf-8").splitlines() if satir.strip()]


def gemini_yurutucu(_hakem: str, sol_png: str, sag_png: str, istem: str) -> str:
    """Agy'yi E: üzerindeki çağrıya özel bir sahnede çalıştırır."""
    kok = os.environ.get("ARENA_AGY_STAGE")
    if not kok:
        raise RuntimeError("ARENA_AGY_STAGE E: üzerindeki bir klasöre ayarlanmalı")
    cozulmus = Path(kok).resolve()
    if cozulmus.drive.upper() != "E:" or str(cozulmus).lower().startswith("~"):
        raise RuntimeError("ARENA_AGY_STAGE E: üzerinde ve ~ dışında olmalı")
    cozulmus.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="arena-agy-", dir=cozulmus) as gecici:
        sol = Path(gecici) / "sol.png"
        sag = Path(gecici) / "sag.png"
        shutil.copyfile(sol_png, sol)
        shutil.copyfile(sag_png, sag)
        gorselli_istem = istem + "\nSol görsel: @sol.png\nSağ görsel: @sag.png"
        komut = ["agy", "--output-format", "text", "--model", "gemini-3.8-flash-high",
                 "--dangerously-skip-permissions", "-p", gorselli_istem]
        sonuc = subprocess.run(komut, cwd=gecici, text=True, encoding="utf-8", errors="replace", capture_output=True, check=True)
        return sonuc.stdout


def sol_yurutucu(_hakem: str, sol_png: str, sag_png: str, istem: str) -> str:
    """Codex'in iki -i girdili, stdin'den tek istem alan ince yürütücüsü."""
    komut = [shutil.which("codex") or "codex", "exec", "--ignore-user-config", "-c", "mcp_servers={}",
             "-c", "features.apps=false", "-m", "gpt-6.1-sol", "-i", sol_png,
             "-i", sag_png, "--skip-git-repo-check", "--color", "never", "-"]
    # ARENA_SOL_EFOR (ör. medium): --ignore-user-config yüzünden efor verilmezse model varsayılanı koşar.
    efor = os.environ.get("ARENA_SOL_EFOR")
    if efor:
        komut[2:2] = ["-c", f"model_reasoning_effort={efor}"]
    sonuc = subprocess.run(komut, input=istem, text=True, encoding="utf-8", errors="replace", capture_output=True, check=True)
    return sonuc.stdout


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ciftler", required=True)
    ap.add_argument("--harita", required=True)
    ap.add_argument("--paftalar", required=True)
    ap.add_argument("--cikis", required=True)
    ap.add_argument("--hakemler", default="gemini,sol")
    a = ap.parse_args()
    ciftler = json.loads(Path(a.ciftler).read_text(encoding="utf-8"))["ciftler"]
    harita = json.loads(Path(a.harita).read_text(encoding="utf-8"))["harita"]
    yurutuculer = {"gemini": gemini_yurutucu, "sol": sol_yurutucu}
    secilen = a.hakemler.split(",")

    def yurut(hakem: str, sol: str, sag: str, istem: str) -> str:
        return yurutuculer[hakem](hakem, sol, sag, istem)

    rapor = hakemleri_kostur(ciftler, harita, a.paftalar, a.cikis, secilen, yurut)
    print(json.dumps(rapor, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()

"""Oylama sayfasının sonuç kodlarını çözer, oyları arena biçimine çevirir.

Kullanım:
  python oylama/coz.py --ciftler ciftler.json --harita gizli_harita.json --cikis insan_oylar.jsonl <kodlar.txt>
kodlar.txt: her satırda bir sonuç kodu (WhatsApp mesajından olduğu gibi yapıştırılabilir; kod satırın içinde aranır).
Kod: ODENA|<set>|<isim>|<oylar>|<sn>|<fnv1a 6 hex>. Sağlama tutmayan ya da çift sayısı uymayan kod REDDEDİLİR, sessiz düşmez.
Çıktı satırı: {"degerlendiren", "set", "cift", "a", "b", "a_etiket", "b_etiket", "sonuc"}  sonuc: 1 = A kazandı, 0 = B, 0.5 = berabere.
"""
import argparse, json, re, sys

DESEN = re.compile(r"ODENA\|[^|\s]+\|[^|]*\|[AB=]*\|\d+\|[0-9a-f]{6}")


def fnv(s):
    h = 0x811c9dc5
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return ("%08x" % h)[:6]


def coz(kod, ciftler, harita):
    parca = kod.split("|")
    govde, saglama = "|".join(parca[:-1]), parca[-1]
    if fnv(govde) != saglama:
        raise ValueError(f"sağlama tutmuyor: {kod[:40]}...")
    _, set_ad, isim, oylar, sn = parca[:5]
    if len(oylar) != len(ciftler):
        raise ValueError(f"{isim}: {len(oylar)} oy, {len(ciftler)} çift bekleniyordu")
    deger = {"A": 1, "B": 0, "=": 0.5}
    return [{"degerlendiren": isim, "set": set_ad, "sure_sn": int(sn), "cift": c["id"], "a": c["a"], "b": c["b"],
             "a_etiket": harita[c["a"]], "b_etiket": harita[c["b"]], "sonuc": deger[o]}
            for c, o in zip(ciftler, oylar)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ciftler", required=True)
    ap.add_argument("--harita", required=True)
    ap.add_argument("--cikis", required=True)
    ap.add_argument("kodlar")
    a = ap.parse_args()
    ciftler = json.load(open(a.ciftler, encoding="utf-8"))
    harita = json.load(open(a.harita, encoding="utf-8"))
    satirlar, hata = [], 0
    for kod in DESEN.findall(open(a.kodlar, encoding="utf-8").read()):
        try:
            satirlar += coz(kod, ciftler, harita)
        except ValueError as e:
            hata += 1
            print("RED:", e, file=sys.stderr)
    with open(a.cikis, "w", encoding="utf-8") as f:
        for s in satirlar:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    kisi = sorted({s["degerlendiren"] for s in satirlar})
    print(f"{len(kisi)} kişi ({', '.join(kisi)}), {len(satirlar)} oy, {hata} reddedilen kod")
    sys.exit(1 if hata else 0)


if __name__ == "__main__":
    main()

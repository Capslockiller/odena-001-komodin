"""Matris özeti: hücre (model x kart) başına ortalama + bootstrap %95 GA, kart etkisi (indeks - yok) farkı, açılan kartlar.

Kullanım: python ozet.py <kosu_klasoru>      (ör. kosular/matris-1; ölçüm <kosu>/olcum/<etiket>/hucre.json)
Çıktı: <kosu>/OZET.md + <kosu>/ozet.json
"""
import glob, json, os, random, re, statistics, sys
from collections import Counter, defaultdict

random.seed(1)
KOK = os.path.abspath(sys.argv[1])
PROJ = os.path.expanduser("~/.claude/projects")

METRIK = [  # (anahtar, başlık, yön: +1 büyük iyi / -1 küçük iyi)
    ("siglip", "SigLIP2 best", +1),
    ("dino", "DINOv2 best", +1),
    ("sekil", "Şekil ort %", -1),
    ("ihlal", "Kontrol ihlali", -1),
    ("ngon", "n-gon", -1),
    ("vertex", "Kafes vertex", 0),
    ("sn", "Süre sn", -1),
    ("cikti_tok", "Çıktı token", -1),
]


def boot(xs, n=2000):
    if len(xs) < 2:
        return (xs[0], xs[0]) if xs else (None, None)
    ms = sorted(statistics.mean(random.choices(xs, k=len(xs))) for _ in range(n))
    return ms[int(n * .025)], ms[int(n * .975)]


def degerler(h, d):
    v = {}
    g = (h.get("gorsel") or {})
    if g.get("siglip2"): v["siglip"] = g["siglip2"]["best"]
    if g.get("dinov2"): v["dino"] = g["dinov2"]["best"]
    s = (h.get("sekil_mesafesi") or {})
    if "biz->usta" in s and "usta->biz" in s:  # iki yön ortalaması, yüksekliğe oran %
        v["sekil"] = 100 * (s["biz->usta"]["ortalama"] + s["usta->biz"]["ortalama"]) / 2
    k = h.get("kontrol") or {}
    if "ihlal_toplam" in k: v["ihlal"] = k["ihlal_toplam"]
    ist = h.get("istatistik") or {}
    if "ngon" in ist: v["ngon"] = ist["ngon"]
    if "ham_v" in ist: v["vertex"] = ist["ham_v"]
    b = os.path.join(d, "bitti.json")
    if os.path.isfile(b): v["sn"] = json.load(open(b, encoding="utf-8"))["sn"]
    v["cikti_tok"] = cikti_token(d)
    return {k2: x for k2, x in v.items() if x is not None}


def cikti_token(d):
    p = os.path.join(d, "cikti.json")
    if os.path.isfile(p):
        try:
            j = json.load(open(p, encoding="utf-8"))
            u = j.get("usage") or {}
            return u.get("output_tokens")
        except Exception:
            return None
    p = os.path.join(d, "cikti.jsonl")
    if os.path.isfile(p):
        for l in open(p, encoding="utf-8", errors="replace"):
            try:
                j = json.loads(l)
            except Exception:
                continue
            if j.get("type") == "turn.completed":
                return (j.get("usage") or {}).get("output_tokens")
    return None


def acilan_kartlar(ad, d):
    """(kart kümesi, kaynak). claude: transkript Read/Bash; codex: komutlar; agy: RAPOR.md (beyan)."""
    k = set()
    sonek = re.sub(r"[^A-Za-z0-9]", "-", os.path.basename(KOK) + "-" + ad)
    tr = sorted(glob.glob(os.path.join(PROJ, f"*-{sonek}", "*.jsonl")), key=os.path.getmtime)[-1:]
    if tr:
        for l in open(tr[0], encoding="utf-8", errors="replace"):
            try:
                j = json.loads(l)
            except Exception:
                continue
            m = j.get("message") or {}
            if m.get("role") != "assistant" or not isinstance(m.get("content"), list):
                continue
            for c in m["content"]:
                if c.get("type") == "tool_use":
                    s = json.dumps(c.get("input"), ensure_ascii=False)
                    if "DIZIN" in s and "kart" not in s.replace("kartlar", ""):
                        continue
                    if "kart" in s:
                        k |= set(re.findall(r"ARS\d-[A-Z]\d+", s))
        return k, "transkript"
    p = os.path.join(d, "cikti.jsonl")
    if os.path.isfile(p):
        for l in open(p, encoding="utf-8", errors="replace"):
            try:
                j = json.loads(l)
            except Exception:
                continue
            it = j.get("item") or {}
            if j.get("type") == "item.completed" and it.get("type") == "command_execution":
                c = it.get("command", "")
                if "kart" in c and "DIZIN" not in c:
                    k |= set(re.findall(r"ARS\d-[A-Z]\d+", c))
        return k, "komut"
    r = os.path.join(d, "RAPOR.md")
    if os.path.isfile(r):
        return set(re.findall(r"ARS\d-[A-Z]\d+", open(r, encoding="utf-8", errors="replace").read())), "beyan"
    return k, "yok"


def main():
    hucre = defaultdict(list)   # (model, kart) -> [degerler]
    kart_say = defaultdict(Counter)
    kart_n = defaultdict(list)
    kirmizi = []
    for hj in sorted(glob.glob(os.path.join(KOK, "olcum*", "*", "hucre.json"))):
        h = json.load(open(hj, encoding="utf-8"))
        ad = h.get("etiket") or os.path.basename(os.path.dirname(hj))
        m = re.match(r"(.+)-([a-z]+)-r(\d+)$", ad)
        if not m:
            continue
        d = os.path.join(KOK, ad)
        if h.get("durum") != "TAMAM":
            kirmizi.append((ad, "; ".join(h.get("sebepler", []))))
            continue
        hucre[(m.group(1), m.group(2))].append(degerler(h, d))
        if m.group(2) == "indeks":
            ks, kay = acilan_kartlar(ad, d)
            kart_n[m.group(1)].append((len(ks), kay))
            kart_say[m.group(1)].update(ks)
    modeller = sorted({k[0] for k in hucre})
    SIRA = ["yok", "indeks", "tarif", "nesne", "referans"]
    kosullar = sorted({k[1] for k in hucre}, key=lambda k: SIRA.index(k) if k in SIRA else 99)
    taban = kosullar[0]
    digerleri = kosullar[1:]
    ozet = {}
    L = [f"# Matris özeti — {os.path.basename(KOK)}", "",
         f"Ortalama [bootstrap %95 GA], n = başarılı tekrar. Fark = koşul − {taban}; GA sıfırı kesiyorsa **kanıt yok**.", ""]
    if kirmizi:
        L += ["## KIRMIZI hücreler", ""] + [f"- {a}: {s}" for a, s in kirmizi] + [""]
    for key, bas, yon in METRIK:
        L += [f"## {bas}", "", "| Model | " + " | ".join(kosullar) + " | " + " | ".join(f"{k}−{taban}" for k in digerleri) + " |",
              "|" + "---|" * (1 + len(kosullar) + len(digerleri))]
        for mo in modeller:
            sat = [mo]
            xs = {}
            for k in kosullar:
                x = [v[key] for v in hucre.get((mo, k), []) if key in v]
                xs[k] = x
                if x:
                    lo, hi = boot(x)
                    sat.append(f"{statistics.mean(x):.3f} [{lo:.3f}–{hi:.3f}] n={len(x)}")
                else:
                    sat.append("-")
                ozet.setdefault(mo, {}).setdefault(k, {})[key] = x
            for k in digerleri:
                if xs[taban] and xs[k]:
                    fs = sorted(statistics.mean(random.choices(xs[k], k=len(xs[k]))) -
                                statistics.mean(random.choices(xs[taban], k=len(xs[taban]))) for _ in range(2000))
                    lo, hi = fs[50], fs[1949]
                    f = statistics.mean(xs[k]) - statistics.mean(xs[taban])
                    kanit = "kanıt yok" if lo <= 0 <= hi else ("iyileşme" if (f > 0) == (yon > 0) and yon else ("kötüleşme" if yon else "fark"))
                    sat.append(f"{f:+.3f} [{lo:+.3f}–{hi:+.3f}] {kanit}")
                else:
                    sat.append("-")
            L.append("| " + " | ".join(sat) + " |")
        L.append("")
    L += ["## Açılan kartlar (indeks koşulu)", ""]
    for mo in modeller:
        n = kart_n.get(mo, [])
        if not n:
            continue
        L.append(f"- **{mo}**: koşu başına {', '.join(str(a) for a, _ in n)} kart (kaynak: {n[0][1]}); en sık: " +
                 ", ".join(f"{k}×{c}" for k, c in kart_say[mo].most_common(12)))
    tum = Counter()
    for c in kart_say.values():
        tum.update(c)
    L += ["", "**Tüm modeller, en sık açılan 20 kart:** " + ", ".join(f"{k}×{c}" for k, c in tum.most_common(20)), ""]
    open(os.path.join(KOK, "OZET.md"), "w", encoding="utf-8").write("\n".join(L))
    json.dump({"hucre": ozet, "kartlar": {m: dict(c) for m, c in kart_say.items()}, "kirmizi": kirmizi},
              open(os.path.join(KOK, "ozet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OZET_OK", os.path.join(KOK, "OZET.md"), "hücre", sum(len(v) for v in hucre.values()), "kırmızı", len(kirmizi))


if __name__ == "__main__":
    main()

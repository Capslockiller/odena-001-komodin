# -*- coding: utf-8 -*-
"""Cok acili goruntu benzerligi. Kaynak mantik: 3DCodeBench metrics/image_similarity.py
(https://github.com/gaoypeng/3dcodebench, arXiv 2606.01057; yerel kopya 30-Kutuphane/Referans/3dcodebench).
Tasinan: encoder siglip2 (get_image_features) ve dinov2 (pooler_output), L2 normalize, 4x4 kosinus matrisi
(render_i x referans_j); view-paired = kosegen ortalamasi; best-assignment = 1-1 eslemenin en iyi ortalamasi.
Degisiklik: scipy linear_sum_assignment yerine 24 permutasyon kaba kuvvet (4x4'te ayni sonuc). Pip kurulumu yok.
Kullanim (venv indeks):
  python gorsel_benzerlik.py --ref <usta cok_aci klasoru> --cikis out.json etiket=<cok_aci klasoru> [...]
Her klasorde v045 v135 v225 v315 .png bulunur.
"""
import argparse, itertools, json, os, sys, time
GORUNUMLER = ["v045.png", "v135.png", "v225.png", "v315.png"]
ENC = {"siglip2": ("google/siglip2-so400m-patch16-naflex", "siglip"),
       "dinov2": ("facebook/dinov2-large", "pooler")}


def yukle(ad, cihaz):
    import torch
    from transformers import AutoModel, AutoProcessor, AutoImageProcessor
    mid, tur = ENC[ad]
    pro = (AutoProcessor if tur == "siglip" else AutoImageProcessor).from_pretrained(mid)
    mod = AutoModel.from_pretrained(mid).to(cihaz).eval()
    return mod, pro, tur


def kodla(mod, pro, tur, klasor, cihaz):
    import torch
    from PIL import Image
    imgs = []
    for g in GORUNUMLER:
        p = os.path.join(klasor, g)
        if not os.path.isfile(p):
            raise FileNotFoundError(p)
        imgs.append(Image.open(p).convert("RGB"))
    giris = pro(images=imgs, return_tensors="pt").to(cihaz)
    with torch.no_grad():
        if tur == "siglip":
            o = mod.get_image_features(**giris)
            f = o if isinstance(o, torch.Tensor) else o.pooler_output
        else:
            f = mod(**giris).pooler_output
    f = f / f.norm(dim=-1, keepdim=True)
    return f.float().cpu()


def skorlar(rend, ref):
    cos = (rend @ ref.T).tolist()  # cos[i][j] = render_i . ref_j
    paired = sum(cos[i][i] for i in range(4)) / 4
    best = max(sum(cos[i][p[i]] for i in range(4)) / 4 for p in itertools.permutations(range(4)))
    return {"paired": round(paired, 6), "best": round(best, 6)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--cikis", required=True)
    ap.add_argument("hucreler", nargs="+")
    a = ap.parse_args()
    import torch
    cihaz = "cuda" if torch.cuda.is_available() else "cpu"
    hd = []
    for s in a.hucreler:
        e, d = s.split("=", 1); hd.append((e, d))
    sonuc = {e: {} for e, _ in hd}
    meta = {"cihaz": cihaz, "yukleme_sn": {}, "kodlama_sn_hucre": {}}
    sure = {e: 0.0 for e, _ in hd}
    for enc in ENC:
        t0 = time.time()
        mod, pro, tur = yukle(enc, cihaz)
        meta["yukleme_sn"][enc] = round(time.time() - t0, 1)
        if cihaz == "cuda":
            torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
        ref = kodla(mod, pro, tur, a.ref, cihaz)
        for e, d in hd:
            t1 = time.time()
            r = kodla(mod, pro, tur, d, cihaz)
            if cihaz == "cuda":
                torch.cuda.synchronize()
            sure[e] += time.time() - t1
            sonuc[e][enc] = skorlar(r, ref)
        if cihaz == "cuda":
            meta.setdefault("gpu_tepe_mb", {})[enc] = round(torch.cuda.max_memory_allocated() / 2**20)
        del mod; torch.cuda.empty_cache() if cihaz == "cuda" else None
    meta["kodlama_sn_hucre"] = {e: round(v, 3) for e, v in sure.items()}
    sonuc["_meta"] = meta
    with open(a.cikis, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print("GORSEL_OK", json.dumps(meta))


if __name__ == "__main__":
    main()

# Arena ligi

Bootstrap: 1000 örnek.

## İnsan ligi

| Model | Elo | %95 GA | Katman |
|---|---:|---:|---:|
| opus-med | 1692.7 | 1478.0–2460.8 | 1 |
| fable-med | 1179.4 | 1009.9–1348.9 | 2 |
| gemini-high | 1139.7 | 961.0–1282.6 | 2 |
| gemini-pro | 966.9 | 770.0–1081.9 | 2 |
| astra-med | 870.9 | 647.1–1006.9 | 3 |
| sol-med | 838.6 | 630.7–953.2 | 3 |
| sonnet-med | 771.5 | 558.4–874.1 | 3 |
| haiku | 540.2 | 230.5–660.3 | 3 |

## Yapay hakem ligi

| Model | Elo | %95 GA | Katman |
|---|---:|---:|---:|
| fable-med | 1475.7 | 1271.8–2761.9 | 1 |
| opus-med | 1152.4 | 914.7–1619.7 | 1 |
| astra-med | 1123.3 | 794.1–1752.6 | 1 |
| sonnet-med | 1049.2 | 684.6–1682.5 | 1 |
| gemini-pro | 988.4 | 298.5–1758.5 | 1 |
| gemini-high | 945.9 | 253.0–1389.6 | 1 |
| sol-med | 785.8 | -15.9–1162.2 | 2 |
| haiku | 479.3 | -1012.7–703.7 | 2 |

## Sayısal ölçütlerin insan Elo geçerliği

| Ölçüt | n | Spearman ρ |
|---|---:|---:|
| dinov2_best | 8 | 0.6190 |
| gorsel.dinov2.best | 8 | 0.6190 |
| gorsel.dinov2.paired | 8 | 0.6190 |
| gorsel.siglip2.best | 8 | 0.5476 |
| gorsel.siglip2.paired | 8 | 0.5476 |
| gorsel_kodlama_sn | 8 | -0.6641 |
| gorsel_render_sn | 8 | 0.2062 |
| gpu_tepe_mb.dinov2 | 8 | — |
| gpu_tepe_mb.siglip2 | 8 | — |
| istatistik.benzersiz_mesh | 8 | 0.1091 |
| istatistik.dortgen | 8 | 0.3333 |
| istatistik.gevsek_vertex | 8 | — |
| istatistik.ham_e | 8 | 0.2143 |
| istatistik.ham_f | 8 | 0.2143 |
| istatistik.ham_v | 8 | 0.2143 |
| istatistik.malzeme | 8 | — |
| istatistik.manifold_disi_kenar | 8 | -0.4124 |
| istatistik.modifier_sayim.BEVEL | 8 | 0.4880 |
| istatistik.modifier_sayim.LATTICE | 1 | — |
| istatistik.modifier_sayim.MIRROR | 1 | — |
| istatistik.modifier_sayim.NODES | 1 | — |
| istatistik.modifier_sayim.SCREW | 1 | — |
| istatistik.modifier_sayim.SOLIDIFY | 3 | — |
| istatistik.modifier_sayim.SUBSURF | 5 | 0.1026 |
| istatistik.modifier_sayim.WEIGHTED_NORMAL | 5 | 0.6669 |
| istatistik.nesne | 8 | 0.1091 |
| istatistik.ngon | 8 | 0.0761 |
| istatistik.olcek_uygulanmamis | 8 | — |
| istatistik.paylasilan_kopya | 8 | — |
| istatistik.son_f | 8 | 0.1429 |
| istatistik.son_ucgen | 8 | 0.0952 |
| istatistik.son_v | 8 | 0.0952 |
| istatistik.ucgen_yuz | 8 | 0.2196 |
| kafes_vertex | 8 | 0.2143 |
| kontrol.hata_veren_kontrol | 8 | — |
| kontrol.ihlal_toplam | 8 | 0.2515 |
| kontrol.ihlalli_kontrol | 8 | -0.6461 |
| kontrol.kontrol_sayisi | 8 | — |
| kontrol_kirmizi | 8 | — |
| oran_biz.ucgen | 8 | 0.0952 |
| oran_usta.ucgen | 8 | — |
| sekil_mesafesi.biz->usta.en_buyuk | 8 | -0.5714 |
| sekil_mesafesi.biz->usta.ortalama | 8 | 0.2857 |
| sekil_mesafesi.biz->usta.p95 | 8 | 0.3095 |
| sekil_mesafesi.usta->biz.en_buyuk | 8 | -0.3333 |
| sekil_mesafesi.usta->biz.ortalama | 8 | 0.2857 |
| sekil_mesafesi.usta->biz.p95 | 8 | 0.0714 |
| sekil_ortalama | 8 | 0.2857 |
| siglip2_best | 8 | 0.5476 |
| tel_vertex | 8 | 0.2143 |
| token.cikti | 8 | 0.3333 |
| token.dusunme | 8 | 0.5714 |
| token.girdi | 8 | 0.1429 |
| token.onbellek_okuma | 8 | 0.2143 |
| token.onbellek_yazma | 4 | -0.4000 |
| token.sure_sn | 6 | 0.1429 |
| token.toplam | 2 | 1.0000 |
| token.usd | 4 | 0.6000 |

## Uyum

```json
{
  "insan": {
    "ortak_cift": 56,
    "yuzde_uyum": 58.92857142857143,
    "krippendorff_alpha": 0.3411612903225807
  },
  "yapay_insan": {
    "ortak_cift": 38,
    "yuzde_uyum": 61.36363636363637,
    "birlesik_krippendorff_alpha": 0.29839347894903456
  }
}
```

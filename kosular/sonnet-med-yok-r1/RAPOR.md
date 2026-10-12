# Molly's Nightstand — rapor

Ölçü: ~0.43 × 0.43 × 0.80 m (tabla taşkın 0.43, gövde en geniş 0.38). Tüm parçalar `Molly's Nightstand` koleksiyonunda; malzeme/renk yok.

## Parçalar ve modifier'lar
| Parça | Yöntem | Modifier |
|---|---|---|
| Body | Yuvarlatılmış kare halkaların (köşe r=3.2 cm) z boyunca dizilip kapatılmasıyla (loft); ortası şişkin, alta doğru 0.38→0.30 m daralıyor | Weighted Normal |
| Top | Aynı loft; üst kenar çeyrek daire (r=2 cm) ile dolgun, alt kenar küçük pah; köşe r≈4.5 cm | Weighted Normal |
| Door, Drawer Front | Gövde bombesini (aynı profil fonksiyonu) izleyen ızgara, gövdeden ~3.5 mm dışarıda; kapak yüksekliği = çekmecenin 2 katı, aralarında 8 mm boşluk | Solidify (12 mm), Bevel (4 mm, 3 seg) |
| Door Knob / Drawer Knob (Shaft + Head) | Kısa silindir mil + basık (Y ölçeği 0.5) UV küre | — |
| Foot ×4 | Aşağı daralan kesik koni (r 3→2 cm), köşelere yakın (±13.5 cm) | Bevel (4 mm, 3 seg) |

## Yöntem
Betik (bmesh) ile parametrik; gövde ve panel aynı `hw_body(t)` profilini kullandığı için paneller bombeyi birebir izler. Workbench önizlemeleriyle ön/yan/izo kontrol edildi.

## Tahminler
- Brief'te tabla kalınlığı yok: ~5.5 cm aldım. Taşma her yönde ~2.5 cm.
- "Yaklaşık 40 cm taban": tabla 43 cm, gövde 38 cm → kaba bir 40 civarı.
- Bombe oranı (alt 30 cm, orta 38 cm, tepe ~35.6 cm), ayak boyu (7.5 cm), topuz boyutu (Ø 4.4 cm) ve boşluk (8 mm) gözle seçildi.
- Gövde içi/çekmece gövdesi modellenmedi (kapalı dış kabuk); paneller gövdenin üstüne oturan ayrı parçalar.

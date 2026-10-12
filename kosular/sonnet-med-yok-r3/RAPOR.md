# RAPOR — Molly's Nightstand

Dosya: `sonuc.blend`, tüm parçalar `Molly's Nightstand` koleksiyonunda. Ölçü metre; toplam 0,44 × 0,44 × 0,80. Malzeme/renk yok. Üretici betik: `build.py`.

## Parçalar ve modifier'lar
| Parça | Açıklama | Modifier |
|---|---|---|
| Body | Gövde: 25 yükseklik halkasından loft; kare, yuvarlatılmış köşeli kesit. Yarı genişlik altta 0,15 → ~%72 yükseklikte 0,19 (bombe) → üstte 0,18. Köşe yarıçapı 0,045 | yok (geometri doğrudan) |
| Top | Tabla 0,44×0,44×0,05, gövdeden ~4 cm taşar. Üst kenar dolgun yuvarlak (r=2 cm), alt kenar küçük pah | yok |
| Drawer Front | Üst çekmece paneli, 0,20×0,19, yuvarlak köşeli, gövde bombesini izler, ~8 mm dışarı taşar | Bevel (3 seg, 4,5 mm) |
| Door | Alt kapak, 0,20×0,385 (çekmecenin ~2 katı), 2 cm boşluk | Bevel |
| Drawer Knob, Door Knob | Basık küre + kısa mil (silindir) | yok |
| Leg.1–4 | Kısa kalın, aşağı daralan ayaklar, köşelere yakın | yok |

## Yöntem
Bmesh ile betikten: bombeli gövde ve tabla/ayaklar yuvarlak köşeli kesit halkalarının loft edilmesi; paneller düz yuvarlak-dikdörtgen yüzün bölünüp her köşe noktasının gövde profiline göre y'de kaydırılması ve içe doğru extrude edilmesiyle. Smooth shading açı tabanlı. Workbench ile 4 açıdan önizleme alıp (persp/ön/yan/arka) kontrol ettim.

## Tahmin ettiğim yerler
- 40 cm taban: tabla 44 cm, gövde en geniş 38 cm, alt 30 cm kabul edildi.
- "Belirgin daralma" ve bombe tepe noktası (%72 yükseklik) ve miktarı (4 cm/yan) tahmin.
- Ayak yüksekliği 9 cm, tabla kalınlığı 5 cm, boşluk 2 cm, topuz çapı ~4,4 cm, mil 1,4 cm çap: brifte yok.
- Paneller gövdenin yan köşe yuvarlamasına girmesin diye 20 cm genişlikte; kenar yumuşatması bevel ile, panel kenar dönüşleri gövdeye gömülü değil bağımsız parça.
- Çekmece/kapak arkası ve içi modellenmedi (kapalı).

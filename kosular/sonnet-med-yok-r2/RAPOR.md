# Molly's Nightstand — RAPOR

Çıktı: `sonuc.blend`, tüm parçalar `Molly's Nightstand` koleksiyonunda. Metre ölçeği, sadece geometri (malzeme/renk yok).
Kutu boyutu: 0.40 × 0.41 × 0.80 m (0.41'in nedeni önde çıkan topuzlar; tabla 0.40 × 0.40). Ön yüz -Y.
Betik: `tmp/build.py`. Önizlemeler: `tmp/*.png`.

## Yöntem
- Gövde, ayaklar ve tabla "halka loft" ile üretildi. Her kesit yuvarlatılmış kare bir halka, yüksekliğe göre boyutu değişiyor, halkalar quad'larla birleştirildi.
- Gövde yarı genişliği profili: altta 13.5 cm, z=0.50'de 17.5 cm (en şişkin nokta), üstte 16.2 cm. Alt yarı yumuşak ease ile belirgin daralıyor. Dikey köşe yarıçapı 4 cm.
- Çekmece ve kapak, gövde profilini izleyen ön yüzey ızgarasından üretildi (x boyunca düz, z'de bombeli). Köşeleri yuvarlatıldı, sonra Solidify ve Bevel eklendi.
- Topuzlar bmesh spin (lathe) ile üretildi: ince mil ve basık topuz tek mesh.

## Parçalar ve modifier'lar
| Parça | Modifier |
|---|---|
| Govde | yok (halka loft, düz gölgelendirme) |
| Tabla (40×40, kalınlık 6 cm, üst kenar R≈2.2 cm yuvarlak, alt kenar 8 mm pah, köşe R 4.5 cm) | Bevel (0.0015 m, 2 segment, açı sınırlı) |
| Ayak_±± (4 adet, 8 cm boy, üstte 7.4 cm → altta 5.2 cm genişlik, köşelere yakın ±10.3 cm) | yok |
| Cekmece_On (18 × 18 cm, z 0.502–0.682) | Solidify (1.2 cm, içe doğru), Bevel (3.5 mm, 3 segment) |
| Kapak_On (18 × 36 cm, z 0.13–0.49, çekmecenin 2 katı yükseklikte) | Solidify, Bevel (aynı) |
| Topuz_Cekmece, Topuz_Kapak (çap 3.7 cm, basık, 3.2 cm çıkıntı) | yok |

Paneller gövdeden 4 mm taşıyor. Aralarında 1.2 cm boşluk var.

## Brief'in boşluk bıraktığı yerler (tahminlerim)
- "Yaklaşık 40 cm taban": tablayı 40 cm aldım. Gövde en şişkin yerinde 35 cm, altta 27 cm. Ayakların tabanı yaklaşık 36 cm.
- Ayak ve tabla yükseklikleri (8 cm ve 6 cm) ile gövdedeki bombe oranı (±4 cm) verilmedi, göz kararı seçtim.
- "Basık çekmece": 18 cm yüksekliğinde. Kapak 36 cm. Boşluk ve taşma miktarı ("çok az", "ince") de tahmin.
- Panel genişliği 18 cm, çünkü gövdenin altta düz kalan ön yüzü o kadar. Daha geniş panel alt köşede yuvarlak yüzeyin dışına taşardı.
- Çekmece ve kapak ayrı kenarlı paneller. İç boşluk, çekmece kutusu ve kapak menteşesi modellenmedi, brief istemedi.
- Mil ve topuz birleşik tek parça. Ayrı parça gerekirse ayrılabilir.

## Kontrol
Ön, yan ve iki perspektif ile alttan görünüş render edildi (Workbench). Bombe silüeti, taşan tabla, panellerin kontura oturması ve ayaklar brief'e uyuyor. Tablanın alt pahı yalnızca yaklaşık 8 mm olduğu için küçük ölçekte zor seçiliyor.

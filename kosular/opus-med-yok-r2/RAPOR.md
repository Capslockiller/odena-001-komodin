# RAPOR — Molly's Nightstand

Dosyalar: `sonuc.blend` (bütün parçalar `Molly's Nightstand` koleksiyonunda), üretici betik `molly.py`, önizlemeler `tmp/prev/*.png`.
Ölçü metre; ön yüz −Y, zemin z = 0. Toplam kutu 0.44 × 0.44 × 0.80 m (tabla dahil; knoplar öne 2.5 cm daha çıkıyor).

## Yöntem
Her parça Python'da açıkça yazılmış profil fonksiyonlarından üretildi:
- **Gövde, tabla, paneller, ayaklar:** yükseklik boyunca sıralanan yuvarlak köşeli dikdörtgen halkaların "loft"u. Bombe, daralma ve kenar yuvarlatmaları halkaların ölçüsünü z'ye göre değiştirerek doğrudan geometriye işlendi. Uçlar n-gon kapakla kapatıldı.
- **Knoplar:** bir yan profilin Y ekseni etrafında döndürülmesi (lathe, 48 dilim).
- Gölgeleme: bütün yüzeyler smooth, 35–40°'den keskin kenarlar sharp olarak işaretlendi. Malzeme/renk yok.

Gövde genişliği w(z): altta 0.335 m, yüksekliğin %60'ında en geniş 0.400 m, tablanın altında 0.384 m (her iki tarafta da tepesi sıfır eğimli iki parabol). Plan kare, yani derinlik de aynı profili izliyor.

## Parçalar ve modifier'lar
| Parça | Açıklama | Modifier |
|---|---|---|
| Body | z 0.08–0.755, bombeli/aşağı daralan, dikey köşe yarıçapı 3.5 cm, alt kenar 8 mm yuvarlak | yok |
| Top | 0.44 × 0.44 × 0.045, plan köşe yarıçapı 4.5 cm, üst kenar 2 cm yuvarlak, alt kenar 7 mm pah | yok |
| Drawer_Front | 18.6 cm yüksek, 1.6 cm kalın, gövdenin ön yüz eğrisini izliyor, kenarlar 6 mm yuvarlak | yok |
| Door | 37.1 cm yüksek (çekmecenin 2 katı), aynı yapı; aradaki boşluk 8 mm | yok |
| Knob_Drawer, Knob_Door | panel ortasında; Ø 13 mm × ~8 mm mil + Ø 43 mm, 1.6 cm kalın basık topuz | yok |
| Leg_FL/FR/BL/BR | 8 cm boy, üstte 6.4 cm → altta 4.8 cm kare kesit, köşe yarıçapı 1.5 cm, alt kenar 5 mm yuvarlak | yok |

Modifier kullanılmadı: yuvarlatma ve bombe profilden üretildiği için Bevel/Subsurf gerekmedi; geometri temiz quad, uygulanmış hâlde.

## Tahmin ettiğim yerler
- "Bombe" yalnız düşey kesitte (yanlar yatayda düz) yorumlandı; en geniş nokta orta-üstte (%60) seçildi, aşağı daralma 6.5 cm.
- "40 × 40 taban" gövdenin en geniş yeri (0.40) olarak alındı; tabla 0.44 ile her yönden 2–5.5 cm taşıyor.
- Tabla kalınlığı 4.5 cm, ayak boyu 8 cm, panel kalınlığı 1.6 cm, kenar paylarının ölçüleri (üst 5, alt 6, yan 4 cm) benim seçimim.
- Ayaklar yuvarlak köşeli kare kesitli seçildi (gövdenin diliyle uyumlu); silindir de olabilirdi.
- Çekmece yalnızca ön panel olarak modellendi (iç kutu/menteşe yok); kapak tek kanat, kulp ortada.
- Panellerin ön görünüşteki köşeleri hafif yuvarlak (6 mm); daha belirgin köşe yuvarlatması istenip istenmediği belirsiz.

## Kontrol
Workbench ile ön, yan, üst ve iki perspektif önizleme alındı; bombe/daralma, tabla taşması, panel oranları, knoplar ve ayaklar brief ile karşılaştırıldı. İlk turda knoplar çivi gibi ince göründüğü için mil kısaltılıp topuz kalınlaştırıldı, ayaklar biraz kalınlaştırıldı.
